"""
File Handler Utilities
Provides file I/O operations for the memory system and data storage.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class FileHandler:
    """
    File handling utilities for reading, writing, and managing files.
    
    Supports:
    - JSON, TXT, YAML file operations
    - Directory management
    - File watching
    - Path resolution
    """
    
    @staticmethod
    def read_text(file_path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Read text file content"""
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def write_text(
        file_path: Union[str, Path],
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> bool:
        """Write text to file"""
        path = Path(file_path)
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        return True
    
    @staticmethod
    def read_json(
        file_path: Union[str, Path],
        encoding: str = "utf-8"
    ) -> Union[Dict, List]:
        """Read JSON file"""
        with open(file_path, "r", encoding=encoding) as f:
            return json.load(f)
    
    @staticmethod
    def write_json(
        file_path: Union[str, Path],
        data: Union[Dict, List],
        indent: int = 2,
        create_dirs: bool = True
    ) -> bool:
        """Write data to JSON file"""
        path = Path(file_path)
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    
    @staticmethod
    def read_yaml(
        file_path: Union[str, Path],
        encoding: str = "utf-8"
    ) -> Dict:
        """Read YAML file"""
        import yaml
        with open(file_path, "r", encoding=encoding) as f:
            return yaml.safe_load(f) or {}
    
    @staticmethod
    def write_yaml(
        file_path: Union[str, Path],
        data: Dict,
        create_dirs: bool = True
    ) -> bool:
        """Write data to YAML file"""
        import yaml
        path = Path(file_path)
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        return True
    
    @staticmethod
    def exists(file_path: Union[str, Path]) -> bool:
        """Check if file exists"""
        return Path(file_path).exists()
    
    @staticmethod
    def delete(file_path: Union[str, Path]) -> bool:
        """Delete file"""
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    
    @staticmethod
    def mkdir(dir_path: Union[str, Path], exist_ok: bool = True) -> bool:
        """Create directory"""
        Path(dir_path).mkdir(parents=True, exist_ok=exist_ok)
        return True
    
    @staticmethod
    def list_files(
        dir_path: Union[str, Path],
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """List files in directory"""
        path = Path(dir_path)
        if not path.exists():
            return []
        
        if recursive:
            return list(path.rglob(pattern))
        else:
            return list(path.glob(pattern))
    
    @staticmethod
    def copy(src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Copy file or directory"""
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            return False
        
        if src_path.is_dir():
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
        
        return True
    
    @staticmethod
    def move(src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Move file or directory"""
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            return False
        
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        return True
    
    @staticmethod
    def get_size(file_path: Union[str, Path]) -> int:
        """Get file size in bytes"""
        return Path(file_path).stat().st_size
    
    @staticmethod
    def get_extension(file_path: Union[str, Path]) -> str:
        """Get file extension"""
        return Path(file_path).suffix
    
    @staticmethod
    def load_config(
        file_path: Union[str, Path],
        default: Optional[Dict] = None
    ) -> Dict:
        """Load configuration file (auto-detect format)"""
        path = Path(file_path)
        
        if not path.exists():
            return default or {}
        
        ext = path.suffix.lower()
        
        if ext == ".json":
            return FileHandler.read_json(path)
        elif ext in [".yaml", ".yml"]:
            return FileHandler.read_yaml(path)
        elif ext == ".txt":
            return {"content": FileHandler.read_text(path)}
        else:
            return {"content": FileHandler.read_text(path)}
