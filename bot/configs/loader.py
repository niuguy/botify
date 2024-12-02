from pathlib import Path
from typing import List
from pydantic import BaseModel
import yaml

class Tool(BaseModel):
    name: str
    enabled: bool
    description: str

class AgentConfig(BaseModel):
    name: str
    description: str
    system_prompt: str
    tools: List[Tool]

class ConfigManager:
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            # Get the current file's directory and navigate to the data subfolder
            current_dir = Path(__file__).parent
            self.config_dir = current_dir / "data"
        else:
            self.config_dir = Path(config_dir)
    
    def load_config(self, name: str) -> AgentConfig:
        """Load agent configuration by name"""
        config_path = self.config_dir / f"{name}.yml"
        if not config_path.exists():
            raise ValueError(f"Configuration '{name}' not found")
        
        with config_path.open() as f:
            config_data = yaml.safe_load(f)
            return AgentConfig(**config_data)
    
    def list_configs(self) -> List[str]:
        """List available configurations"""
        return [f.stem for f in self.config_dir.glob("*.yml")]
    
    def save_config(self, config: AgentConfig):
        """Save agent configuration"""
        config_path = self.config_dir / f"{config.name}.yml"
        with config_path.open('w') as f:
            yaml.dump(config.dict(), f)