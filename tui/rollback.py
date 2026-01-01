"""
Rollback and Undo System for Destructive Operations
"""

import os
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class Operation:
    """Represents a tracked operation"""
    operation_id: str
    operation_type: str
    file_path: str
    timestamp: str
    old_content: str
    new_content: str
    metadata: Dict[str, Any]
    description: str = ""


class RollbackManager:
    """Manages rollback and undo capabilities"""
    
    def __init__(self, root_dir: str, max_snapshots: int = 50):
        self.root_dir = Path(root_dir)
        self.snapshot_dir = self.root_dir / '.blonde' / 'snapshots'
        self.max_snapshots = max_snapshots
        self.operation_log_file = self.snapshot_dir / 'operations.jsonl'
        self.current_operations: List[Operation] = []
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the rollback system"""
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        if self.operation_log_file.exists():
            self._load_operations()
    
    def _load_operations(self):
        """Load operations from log file"""
        try:
            with open(self.operation_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        op_data = json.loads(line)
                        op = Operation(**op_data)
                        self.current_operations.append(op)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load operation log: {e}[/yellow]")
    
    def _save_operation(self, operation: Operation):
        """Save operation to log"""
        with open(self.operation_log_file, 'a') as f:
            f.write(json.dumps(asdict(operation)) + '\n')
        self.current_operations.append(operation)
        
        # Cleanup old operations if needed
        self._cleanup_old_operations()
    
    def _cleanup_old_operations(self):
        """Remove old operations exceeding max_snapshots"""
        if len(self.current_operations) > self.max_snapshots:
            # Remove oldest operations
            ops_to_remove = self.current_operations[:-self.max_snapshots]
            for op in ops_to_remove:
                snapshot_path = self._get_snapshot_path(op.operation_id)
                if snapshot_path.exists():
                    snapshot_path.unlink()
            
            self.current_operations = self.current_operations[-self.max_snapshots:]
            
            # Rebuild log file
            with open(self.operation_log_file, 'w') as f:
                for op in self.current_operations:
                    f.write(json.dumps(asdict(op)) + '\n')
    
    def _get_snapshot_path(self, operation_id: str) -> Path:
        """Get path to snapshot file"""
        return self.snapshot_dir / f"{operation_id}.snapshot"
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        timestamp = datetime.now().isoformat()
        content = f"{timestamp}_{len(self.current_operations)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def track_operation(self, operation_type: str, file_path: str, 
                       old_content: str, new_content: str,
                       description: str = "", **metadata) -> str:
        """Track an operation for potential rollback"""
        operation_id = self._generate_operation_id()
        
        # Save snapshot of old content
        snapshot_path = self._get_snapshot_path(operation_id)
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            f.write(old_content)
        
        operation = Operation(
            operation_id=operation_id,
            operation_type=operation_type,
            file_path=str(file_path),
            timestamp=datetime.now().isoformat(),
            old_content=old_content,
            new_content=new_content,
            metadata=metadata,
            description=description
        )
        
        self._save_operation(operation)
        console.print(f"[green]Tracked operation: {operation_id[:8]}[/green]")
        
        return operation_id
    
    def rollback_operation(self, operation_id: str) -> bool:
        """Rollback a specific operation"""
        operation = None
        for op in self.current_operations:
            if op.operation_id == operation_id:
                operation = op
                break
        
        if not operation:
            console.print(f"[red]Operation not found: {operation_id}[/red]")
            return False
        
        try:
            file_path = Path(operation.file_path)
            
            # Restore from snapshot
            snapshot_path = self._get_snapshot_path(operation_id)
            if not snapshot_path.exists():
                console.print(f"[red]Snapshot not found for operation: {operation_id}[/red]")
                return False
            
            # Create backup before rollback
            backup_path = file_path.with_suffix(f"{file_path.suffix}.rollback_backup")
            shutil.copy2(file_path, backup_path)
            
            # Restore content
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(old_content)
            
            console.print(f"[green]Rolled back operation: {operation_id[:8]}[/green]")
            console.print(f"[dim]Backup saved to: {backup_path}[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]Rollback failed: {e}[/red]")
            return False
    
    def rollback_to_snapshot(self, snapshot_name: str) -> bool:
        """Rollback entire project to a named snapshot"""
        snapshot_path = self.snapshot_dir / f"{snapshot_name}.tar.gz"
        
        if not snapshot_path.exists():
            console.print(f"[red]Snapshot not found: {snapshot_name}[/red]")
            return False
        
        try:
            # Create backup of current state
            current_snapshot = f"before_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.create_snapshot(current_snapshot)
            
            # Extract snapshot
            import tarfile
            with tarfile.open(snapshot_path, 'r:gz') as tar:
                tar.extractall(path=self.root_dir)
            
            console.print(f"[green]Restored snapshot: {snapshot_name}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Snapshot restore failed: {e}[/red]")
            return False
    
    def create_snapshot(self, snapshot_name: str) -> bool:
        """Create a full project snapshot"""
        snapshot_path = self.snapshot_dir / f"{snapshot_name}.tar.gz"
        
        try:
            import tarfile
            
            with tarfile.open(snapshot_path, 'w:gz') as tar:
                for item in self.root_dir.iterdir():
                    # Skip the snapshots directory itself
                    if item.name == '.blonde':
                        continue
                    if item.is_file():
                        tar.add(item, arcname=item.name)
                    elif item.is_dir():
                        tar.add(item, arcname=item.name, 
                               filter=lambda x: None if '.blonde' in x.name else x)
            
            console.print(f"[green]Snapshot created: {snapshot_name}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Snapshot creation failed: {e}[/red]")
            return False
    
    def list_snapshots(self) -> List[str]:
        """List all available snapshots"""
        snapshots = []
        
        for item in self.snapshot_dir.glob('*.tar.gz'):
            snapshots.append(item.stem)
        
        return sorted(snapshots, reverse=True)
    
    def list_operations(self, limit: int = 10) -> List[Operation]:
        """List recent operations"""
        return self.current_operations[-limit:]
    
    def undo_last(self) -> bool:
        """Undo the last operation"""
        if not self.current_operations:
            console.print("[yellow]No operations to undo[/yellow]")
            return False
        
        last_op = self.current_operations[-1]
        return self.rollback_operation(last_op.operation_id)
    
    def get_operation_history(self) -> Table:
        """Get formatted operation history"""
        table = Table(title="Operation History")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("File", style="yellow")
        table.add_column("Time", style="blue")
        table.add_column("Description")
        
        for op in reversed(self.current_operations[-10:]):
            table.add_row(
                op.operation_id[:8],
                op.operation_type,
                Path(op.file_path).name,
                op.timestamp[:19].replace('T', ' '),
                op.description[:50] + "..." if len(op.description) > 50 else op.description
            )
        
        return table
    
    def clear_history(self) -> bool:
        """Clear all operation history"""
        try:
            # Remove all snapshots
            for snapshot in self.snapshot_dir.glob('*.snapshot'):
                snapshot.unlink()
            
            # Clear operation log
            if self.operation_log_file.exists():
                self.operation_log_file.unlink()
            
            self.current_operations = []
            console.print("[green]Operation history cleared[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Failed to clear history: {e}[/red]")
            return False


class SafeFileEditor:
    """File editor with automatic rollback support"""
    
    def __init__(self, rollback_manager: RollbackManager):
        self.rollback_manager = rollback_manager
    
    def edit_file(self, file_path: str, new_content: str, 
                 operation_type: str = "edit", description: str = "") -> bool:
        """Safely edit a file with automatic tracking"""
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                console.print(f"[red]File not found: {file_path}[/red]")
                return False
            
            # Read current content
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                old_content = f.read()
            
            # Track the operation
            self.rollback_manager.track_operation(
                operation_type=operation_type,
                file_path=file_path,
                old_content=old_content,
                new_content=new_content,
                description=description or f"Edit {file_path_obj.name}"
            )
            
            # Write new content
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            console.print(f"[red]Edit failed: {e}[/red]")
            return False
    
    def delete_file(self, file_path: str, description: str = "") -> bool:
        """Safely delete a file with tracking"""
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                console.print(f"[red]File not found: {file_path}[/red]")
                return False
            
            # Read current content
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                old_content = f.read()
            
            # Track the operation
            self.rollback_manager.track_operation(
                operation_type="delete",
                file_path=file_path,
                old_content=old_content,
                new_content="",
                description=description or f"Delete {file_path_obj.name}"
            )
            
            # Delete the file
            file_path_obj.unlink()
            
            console.print(f"[green]Deleted: {file_path}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Delete failed: {e}[/red]")
            return False
    
    def rename_file(self, old_path: str, new_path: str, 
                   description: str = "") -> bool:
        """Safely rename a file with tracking"""
        try:
            old_path_obj = Path(old_path)
            new_path_obj = Path(new_path)
            
            if not old_path_obj.exists():
                console.print(f"[red]File not found: {old_path}[/red]")
                return False
            
            # Read current content
            with open(old_path_obj, 'r', encoding='utf-8') as f:
                old_content = f.read()
            
            # Track the operation
            self.rollback_manager.track_operation(
                operation_type="rename",
                file_path=old_path,
                old_content=old_content,
                new_content="",
                description=description or f"Rename {old_path_obj.name} -> {new_path_obj.name}",
                old_file_path=old_path,
                new_file_path=new_path
            )
            
            # Rename the file
            old_path_obj.rename(new_path_obj)
            
            console.print(f"[green]Renamed: {old_path} -> {new_path}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Rename failed: {e}[/red]")
            return False


def create_rollback_manager(root_dir: str) -> RollbackManager:
    """Factory function to create a rollback manager"""
    return RollbackManager(root_dir)
