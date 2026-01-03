"""
Cost Tracker - Track API usage costs in USD
Supports multiple providers with different pricing models
"""

from pathlib import Path
from typing import Dict, Optional
import json
from rich.console import Console

console = Console()


class CostTracker:
    """Tracks AI API costs across providers and models"""
    
    # Pricing data (input tokens per 1M, output tokens per 1M)
    PRICING = {
        "openrouter": {
            "openai/gpt-4": {"input": 30.0, "output": 60.0},
            "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "openai/gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "anthropic/claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
            "anthropic/claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
            "mistralai/mistral-large": {"input": 4.0, "output": 12.0},
            "google/gemini-pro": {"input": 0.5, "output": 1.5},
            "meta-llama/llama-2-70b-chat": {"input": 0.9, "output": 0.9}
        },
        "openai": {
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "gpt-4-turbo-preview": {"input": 10.0, "output": 30.0}
        },
        "anthropic": {
            "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
            "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25}
        },
        "local": {
            "default": {"input": 0.0, "output": 0.0}  # Free
        }
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (Path.home() / ".blonde" / "costs.json")
        self.session_costs: Dict[str, Dict] = {}
        
        self._load_costs()
    
    def _load_costs(self):
        """Load cost tracking data from disk"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.session_costs = json.load(f)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load cost data: {e}[/yellow]")
    
    def _save_costs(self):
        """Save cost tracking data to disk"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.session_costs, f, indent=2)
        except Exception as e:
            console.print(f"[red]Failed to save cost data: {e}[/red]")
    
    def calculate_cost(self, provider: str, model: str, 
                   input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost for API usage
        
        Args:
            provider: AI provider name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Cost in USD
        """
        # Get pricing for provider/model
        pricing = self.PRICING.get(provider, {})
        model_pricing = pricing.get(model, pricing.get("default", {"input": 0.0, "output": 0.0}))
        
        # Calculate cost (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * model_pricing.get("input", 0.0)
        output_cost = (output_tokens / 1_000_000) * model_pricing.get("output", 0.0)
        
        total_cost = input_cost + output_cost
        
        return round(total_cost, 6)  # Round to 6 decimal places
    
    def track_usage(self, session_id: str, provider: str, model: str,
                  input_tokens: int, output_tokens: int) -> float:
        """
        Track usage and return cost
        
        Args:
            session_id: Session identifier
            provider: AI provider
            model: Model name
            input_tokens: Input tokens used
            output_tokens: Output tokens used
        
        Returns:
            Cost in USD
        """
        cost = self.calculate_cost(provider, model, input_tokens, output_tokens)
        
        # Initialize session if not exists
        if session_id not in self.session_costs:
            self.session_costs[session_id] = {
                "total_usd": 0.0,
                "by_provider": {},
                "by_model": {},
                "usage_count": 0
            }
        
        session_data = self.session_costs[session_id]
        
        # Update total
        session_data["total_usd"] += cost
        session_data["usage_count"] += 1
        
        # Track by provider
        if provider not in session_data["by_provider"]:
            session_data["by_provider"][provider] = {
                "total_usd": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "usage_count": 0
            }
        
        provider_data = session_data["by_provider"][provider]
        provider_data["total_usd"] += cost
        provider_data["input_tokens"] += input_tokens
        provider_data["output_tokens"] += output_tokens
        provider_data["usage_count"] += 1
        
        # Track by model
        model_key = f"{provider}/{model}"
        if model_key not in session_data["by_model"]:
            session_data["by_model"][model_key] = {
                "total_usd": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "usage_count": 0
            }
        
        model_data = session_data["by_model"][model_key]
        model_data["total_usd"] += cost
        model_data["input_tokens"] += input_tokens
        model_data["output_tokens"] += output_tokens
        model_data["usage_count"] += 1
        
        self._save_costs()
        
        return cost
    
    def get_session_cost(self, session_id: str) -> Dict:
        """
        Get cost breakdown for a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dict with cost breakdown
        """
        if session_id not in self.session_costs:
            return {
                "total_usd": 0.0,
                "by_provider": {},
                "by_model": {},
                "usage_count": 0
            }
        
        return self.session_costs[session_id]
    
    def get_total_cost(self) -> Dict:
        """
        Get total cost across all sessions
        
        Returns:
            Dict with total cost breakdown
        """
        total_usd = 0.0
        by_provider = {}
        by_model = {}
        total_usage_count = 0
        
        for session_id, session_data in self.session_costs.items():
            total_usd += session_data["total_usd"]
            total_usage_count += session_data["usage_count"]
            
            # Aggregate by provider
            for provider, provider_data in session_data["by_provider"].items():
                if provider not in by_provider:
                    by_provider[provider] = {
                        "total_usd": 0.0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "usage_count": 0
                    }
                by_provider[provider]["total_usd"] += provider_data["total_usd"]
                by_provider[provider]["input_tokens"] += provider_data["input_tokens"]
                by_provider[provider]["output_tokens"] += provider_data["output_tokens"]
                by_provider[provider]["usage_count"] += provider_data["usage_count"]
            
            # Aggregate by model
            for model_key, model_data in session_data["by_model"].items():
                if model_key not in by_model:
                    by_model[model_key] = {
                        "total_usd": 0.0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "usage_count": 0
                    }
                by_model[model_key]["total_usd"] += model_data["total_usd"]
                by_model[model_key]["input_tokens"] += model_data["input_tokens"]
                by_model[model_key]["output_tokens"] += model_data["output_tokens"]
                by_model[model_key]["usage_count"] += model_data["usage_count"]
        
        return {
            "total_usd": total_usd,
            "by_provider": by_provider,
            "by_model": by_model,
            "usage_count": total_usage_count
        }
    
    def estimate_next_cost(self, provider: str, model: str, 
                        estimated_input_tokens: int, 
                        estimated_output_tokens: int) -> Dict:
        """
        Estimate cost for next prompt
        
        Args:
            provider: AI provider
            model: Model name
            estimated_input_tokens: Estimated input tokens
            estimated_output_tokens: Estimated output tokens
        
        Returns:
            Dict with cost estimate
        """
        cost = self.calculate_cost(
            provider, model, 
            estimated_input_tokens, estimated_output_tokens
        )
        
        # Get historical average if available
        total_data = self.get_total_cost()
        avg_cost_per_request = 0.0
        if total_data["usage_count"] > 0:
            avg_cost_per_request = total_data["total_usd"] / total_data["usage_count"]
        
        return {
            "estimated_cost_usd": cost,
            "avg_cost_per_request_usd": avg_cost_per_request,
            "input_tokens": estimated_input_tokens,
            "output_tokens": estimated_output_tokens,
            "difference_from_average": cost - avg_cost_per_request
        }
    
    def add_custom_pricing(self, provider: str, model: str, 
                         input_price: float, output_price: float):
        """
        Add or update custom pricing for a model
        
        Args:
            provider: AI provider
            model: Model name
            input_price: Price per 1M input tokens
            output_price: Price per 1M output tokens
        """
        if provider not in self.PRICING:
            self.PRICING[provider] = {}
        
        self.PRICING[provider][model] = {
            "input": input_price,
            "output": output_price
        }
        
        console.print(f"[green]✓ Added custom pricing:[/green] {provider}/{model}")
    
    def get_pricing_info(self, provider: str, model: str) -> Dict:
        """
        Get pricing information for a model
        
        Args:
            provider: AI provider
            model: Model name
        
        Returns:
            Dict with pricing info
        """
        pricing = self.PRICING.get(provider, {})
        model_pricing = pricing.get(model, {})
        
        if not model_pricing:
            return None
        
        return {
            "provider": provider,
            "model": model,
            "input_price_per_1m": model_pricing["input"],
            "output_price_per_1m": model_pricing["output"],
            "input_price_per_1k": round(model_pricing["input"] / 1000, 4),
            "output_price_per_1k": round(model_pricing["output"] / 1000, 4)
        }
    
    def list_pricing(self, provider: Optional[str] = None) -> Dict:
        """
        List all pricing or pricing for a specific provider
        
        Args:
            provider: Optional provider to filter by
        
        Returns:
            Dict with pricing information
        """
        if provider:
            return self.PRICING.get(provider, {})
        
        return self.PRICING


# Global cost tracker instance
cost_tracker = CostTracker()


def get_cost_tracker() -> CostTracker:
    """Get the global cost tracker instance"""
    return cost_tracker


if __name__ == "__main__":
    # Demo Cost Tracker
    tracker = CostTracker()
    
    print("=== Cost Tracker Demo ===\n")
    
    # Track some usage
    cost1 = tracker.track_usage(
        "session1", "openrouter", "openai/gpt-4", 
        1000, 500
    )
    print(f"Cost 1: ${cost1:.6f}")
    
    cost2 = tracker.track_usage(
        "session1", "openrouter", "openai/gpt-4",
        500, 300
    )
    print(f"Cost 2: ${cost2:.6f}")
    
    cost3 = tracker.track_usage(
        "session2", "openai", "gpt-3.5-turbo",
        2000, 1000
    )
    print(f"Cost 3: ${cost3:.6f}")
    
    # Get session cost
    print("\nSession 1 cost:")
    session_cost = tracker.get_session_cost("session1")
    print(f"  Total: ${session_cost['total_usd']:.6f}")
    print(f"  Requests: {session_cost['usage_count']}")
    
    # Get total cost
    print("\nTotal cost:")
    total = tracker.get_total_cost()
    print(f"  Total: ${total['total_usd']:.6f}")
    print(f"  Requests: {total['usage_count']}")
    
    # Estimate next cost
    print("\nEstimate next cost:")
    estimate = tracker.estimate_next_cost(
        "openrouter", "openai/gpt-4", 1500, 800
    )
    print(f"  Estimated: ${estimate['estimated_cost_usd']:.6f}")
    print(f"  Average: ${estimate['avg_cost_per_request_usd']:.6f}")
