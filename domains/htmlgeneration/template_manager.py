"""
Template manager for handling HTML templates and static resources.
"""

import os
import logging
from typing import Optional


class TemplateManager:
    """
    Manages HTML templates and static resource URLs.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the template manager.
        
        Args:
            logger: Logger instance (optional)
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.template_path = "functions/linuxaio_template.html"
        self.static_url = "/static/report_style.css"
        self.js_static_url = "/static/script_report.js"
    
    def load_template(self) -> str:
        """
        Load the base HTML template.
        
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If template file cannot be read
        """
        try:
            if not os.path.exists(self.template_path):
                raise FileNotFoundError(f"Template file not found: {self.template_path}")
            
            with open(self.template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.debug(f"Loaded template from {self.template_path}")
            return content
            
        except IOError as e:
            raise IOError(f"Failed to read template file: {e}")
    
    def inject_static_resources(self, content: str) -> str:
        """
        Inject static CSS and JavaScript resources into the template.
        
        Args:
            content: Template content
            
        Returns:
            Template content with injected resources
        """
        # Inject CSS - this should be injected at the beginning of head
        css_injection = f'<link rel="stylesheet" type="text/css" href="{self.static_url}">'
        content = content.replace("<!-- header.script1_placeholder -->", css_injection)
        
        # Inject JavaScript - this should be injected after the font-awesome link
        js_injection = f'<script src="{self.js_static_url}" type="text/javascript"></script>'
        content = content.replace("<!-- header.script2_placeholder -->", js_injection)
        
        self.logger.debug("Injected static resources into template")
        return content
    
    def inject_version_info(self, content: str, version: str) -> str:
        """
        Inject version information into the template.
        
        Args:
            content: Template content
            version: Version string
            
        Returns:
            Template content with version info
        """
        version_info = f'<p>| WebApp v{version}</p>'
        content = content.replace("<!-- footer.version_placeholder -->", version_info)
        
        self.logger.debug(f"Injected version info: {version}")
        return content
