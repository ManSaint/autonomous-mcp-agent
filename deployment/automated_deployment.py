"""
🚀 PHASE 9: Automated Enterprise Deployment
One-click deployment with validated 15-server ecosystem

This module provides automated deployment capabilities for the enterprise
MCP platform with validated integrations, containerization, and cloud
deployment support.
"""

import asyncio
import json
import logging
import subprocess
import shutil
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
import tempfile

class AutomatedDeployment:
    """
    📦 Automated Enterprise Deployment
    
    Provides one-click deployment for the enterprise MCP platform with
    complete 15-server ecosystem, containerization, and cloud support.
    """
    
    def __init__(self, project_root: str):
        self.logger = logging.getLogger(__name__)
        self.project_root = Path(project_root)
        
        # Deployment configuration
        self.deployment_config = {
            "version": "9.0.0",
            "platform": "enterprise_mcp",
            "servers_count": 15,
            "tools_count": 202,
            "deployment_types": ["docker", "kubernetes", "cloud"]
        }
        
        # Validated server configurations from Phase 8.9
        self.validated_servers = [
            "github", "postman", "trello", "youtube", "commander",
            "memory", "browser", "magicui", "taskmaster", "toolagent", 
            "artifacts", "web_search", "movies", "mcp_tools", "autonomous"
        ]
        
        self.logger.info("📦 Automated Deployment initialized")
    
    async def create_deployment_package(self) -> str:
        """Create complete deployment package"""
        try:
            self.logger.info("🔄 Creating enterprise deployment package...")
            
            # Create deployment directory
            deployment_dir = self.project_root / "deployment_package"
            deployment_dir.mkdir(exist_ok=True)
            
            # Copy core application files
            await self._copy_application_files(deployment_dir)
            
            # Generate configuration files
            await self._generate_deployment_configs(deployment_dir)
            
            # Create Docker configurations
            await self._create_docker_configs(deployment_dir)
            
            # Create Kubernetes manifests
            await self._create_kubernetes_configs(deployment_dir)
            
            # Create cloud deployment templates
            await self._create_cloud_configs(deployment_dir)
            
            # Generate deployment documentation
            await self._generate_deployment_docs(deployment_dir)
            
            self.logger.info(f"✅ Deployment package created: {deployment_dir}")
            return str(deployment_dir)
            
        except Exception as e:
            self.logger.error(f"❌ Deployment package creation failed: {str(e)}")
            raise
    
    async def _copy_application_files(self, deployment_dir: Path):
        """Copy essential application files"""
        try:
            # Create application structure
            app_dir = deployment_dir / "app"
            app_dir.mkdir(exist_ok=True)
            
            # Copy autonomous_mcp directory
            if (self.project_root / "autonomous_mcp").exists():
                shutil.copytree(
                    self.project_root / "autonomous_mcp",
                    app_dir / "autonomous_mcp",
                    dirs_exist_ok=True
                )
            
            # Copy enterprise directory
            if (self.project_root / "enterprise").exists():
                shutil.copytree(
                    self.project_root / "enterprise", 
                    app_dir / "enterprise",
                    dirs_exist_ok=True
                )
            
            # Copy interfaces directory
            if (self.project_root / "interfaces").exists():
                shutil.copytree(
                    self.project_root / "interfaces",
                    app_dir / "interfaces", 
                    dirs_exist_ok=True
                )
            
            # Copy requirements files
            for req_file in ["requirements.txt", "requirements_mcp.txt"]:
                if (self.project_root / req_file).exists():
                    shutil.copy2(self.project_root / req_file, app_dir)
            
            self.logger.info("📁 Application files copied to deployment package")
            
        except Exception as e:
            self.logger.error(f"❌ Application file copy failed: {str(e)}")
            raise
    
    async def _generate_deployment_configs(self, deployment_dir: Path):
        """Generate deployment configuration files"""
        try:
            config_dir = deployment_dir / "config"
            config_dir.mkdir(exist_ok=True)
            
            # Main deployment configuration
            main_config = {
                "deployment": {
                    "name": "enterprise-mcp-platform",
                    "version": self.deployment_config["version"],
                    "description": "Enterprise MCP Platform with 15 servers and 202 tools"
                },
                "servers": {
                    "validated_servers": self.validated_servers,
                    "total_count": len(self.validated_servers)
                },
                "services": {
                    "orchestrator": {"port": 8000, "replicas": 2},
                    "api": {"port": 8001, "replicas": 3},
                    "dashboard": {"port": 8002, "replicas": 2},
                    "monitoring": {"port": 8003, "replicas": 1}
                },
                "security": {
                    "enable_tls": True,
                    "api_key_required": True,
                    "audit_logging": True
                },
                "performance": {
                    "connection_pooling": True,
                    "caching_enabled": True,
                    "optimization_level": "enterprise"
                }
            }
            
            with open(config_dir / "deployment.yaml", 'w') as f:
                yaml.dump(main_config, f, default_flow_style=False)
            
            # Environment configuration template
            env_config = {
                "environment": "production",
                "log_level": "INFO",
                "database_url": "${DATABASE_URL}",
                "redis_url": "${REDIS_URL}",
                "github_token": "${GITHUB_TOKEN}",
                "postman_api_key": "${POSTMAN_API_KEY}",
                "trello_api_key": "${TRELLO_API_KEY}",
                "encryption_key": "${ENCRYPTION_KEY}"
            }
            
            with open(config_dir / "environment.yaml", 'w') as f:
                yaml.dump(env_config, f, default_flow_style=False)
            
            self.logger.info("⚙️ Deployment configurations generated")
            
        except Exception as e:
            self.logger.error(f"❌ Configuration generation failed: {str(e)}")
            raise
    
    async def _create_docker_configs(self, deployment_dir: Path):
        """Create Docker deployment configurations"""
        try:
            docker_dir = deployment_dir / "docker"
            docker_dir.mkdir(exist_ok=True)
            
            # Main Dockerfile
            dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY app/requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements_mcp.txt

# Copy application code
COPY app/ ./

# Create non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose ports
EXPOSE 8000 8001 8002 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command
CMD ["python", "-m", "interfaces.web_dashboard"]
"""
            
            with open(docker_dir / "Dockerfile", 'w') as f:
                f.write(dockerfile_content.strip())
            
            # Docker Compose configuration
            docker_compose = {
                "version": "3.8",
                "services": {
                    "enterprise-mcp": {
                        "build": {"context": "..", "dockerfile": "docker/Dockerfile"},
                        "ports": ["8000:8000", "8001:8001", "8002:8002"],
                        "environment": [
                            "ENVIRONMENT=production",
                            "LOG_LEVEL=INFO"
                        ],
                        "volumes": ["./data:/app/data"],
                        "restart": "unless-stopped",
                        "healthcheck": {
                            "test": ["CMD", "curl", "-f", "http://localhost:8000/api/health"],
                            "interval": "30s",
                            "timeout": "10s",
                            "retries": 3
                        }
                    },
                    "redis": {
                        "image": "redis:7-alpine",
                        "ports": ["6379:6379"],
                        "volumes": ["redis_data:/data"],
                        "restart": "unless-stopped"
                    },
                    "postgres": {
                        "image": "postgres:15-alpine", 
                        "environment": [
                            "POSTGRES_DB=enterprise_mcp",
                            "POSTGRES_USER=mcpuser",
                            "POSTGRES_PASSWORD=mcppassword"
                        ],
                        "volumes": ["postgres_data:/var/lib/postgresql/data"],
                        "restart": "unless-stopped"
                    }
                },
                "volumes": {
                    "redis_data": {},
                    "postgres_data": {}
                }
            }
            
            with open(docker_dir / "docker-compose.yml", 'w') as f:
                yaml.dump(docker_compose, f, default_flow_style=False)
            
            # Docker deployment script
            deploy_script = """#!/bin/bash
set -e

echo "🚀 Starting Enterprise MCP Platform deployment..."

# Build and start services
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Health check
echo "🔍 Performing health check..."
curl -f http://localhost:8000/api/health

echo "✅ Enterprise MCP Platform deployed successfully!"
echo "📊 Dashboard: http://localhost:8000"
echo "🌐 API: http://localhost:8001/api/docs"
"""
            
            deploy_script_path = docker_dir / "deploy.sh"
            with open(deploy_script_path, 'w') as f:
                f.write(deploy_script.strip())
            deploy_script_path.chmod(0o755)
            
            self.logger.info("🐳 Docker configurations created")
            
        except Exception as e:
            self.logger.error(f"❌ Docker configuration creation failed: {str(e)}")
            raise
    
    async def _create_kubernetes_configs(self, deployment_dir: Path):
        """Create Kubernetes deployment manifests"""
        try:
            k8s_dir = deployment_dir / "kubernetes"
            k8s_dir.mkdir(exist_ok=True)
            
            # Namespace
            namespace = {
                "apiVersion": "v1",
                "kind": "Namespace", 
                "metadata": {"name": "enterprise-mcp"}
            }
            
            with open(k8s_dir / "namespace.yaml", 'w') as f:
                yaml.dump(namespace, f, default_flow_style=False)
            
            # ConfigMap
            configmap = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": "enterprise-mcp-config",
                    "namespace": "enterprise-mcp"
                },
                "data": {
                    "ENVIRONMENT": "production",
                    "LOG_LEVEL": "INFO",
                    "SERVERS_COUNT": "15",
                    "TOOLS_COUNT": "202"
                }
            }
            
            with open(k8s_dir / "configmap.yaml", 'w') as f:
                yaml.dump(configmap, f, default_flow_style=False)
            
            # Deployment
            deployment = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "enterprise-mcp",
                    "namespace": "enterprise-mcp"
                },
                "spec": {
                    "replicas": 3,
                    "selector": {"matchLabels": {"app": "enterprise-mcp"}},
                    "template": {
                        "metadata": {"labels": {"app": "enterprise-mcp"}},
                        "spec": {
                            "containers": [{
                                "name": "enterprise-mcp",
                                "image": "enterprise-mcp:latest",
                                "ports": [
                                    {"containerPort": 8000},
                                    {"containerPort": 8001},
                                    {"containerPort": 8002}
                                ],
                                "envFrom": [{"configMapRef": {"name": "enterprise-mcp-config"}}],
                                "livenessProbe": {
                                    "httpGet": {"path": "/api/health", "port": 8000},
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 30
                                },
                                "readinessProbe": {
                                    "httpGet": {"path": "/api/health", "port": 8000},
                                    "initialDelaySeconds": 10,
                                    "periodSeconds": 10
                                }
                            }]
                        }
                    }
                }
            }
            
            with open(k8s_dir / "deployment.yaml", 'w') as f:
                yaml.dump(deployment, f, default_flow_style=False)
            
            # Service
            service = {
                "apiVersion": "v1", 
                "kind": "Service",
                "metadata": {
                    "name": "enterprise-mcp-service",
                    "namespace": "enterprise-mcp"
                },
                "spec": {
                    "selector": {"app": "enterprise-mcp"},
                    "ports": [
                        {"name": "dashboard", "port": 8000, "targetPort": 8000},
                        {"name": "api", "port": 8001, "targetPort": 8001},
                        {"name": "monitoring", "port": 8002, "targetPort": 8002}
                    ],
                    "type": "LoadBalancer"
                }
            }
            
            with open(k8s_dir / "service.yaml", 'w') as f:
                yaml.dump(service, f, default_flow_style=False)
            
            self.logger.info("☸️ Kubernetes configurations created")
            
        except Exception as e:
            self.logger.error(f"❌ Kubernetes configuration creation failed: {str(e)}")
            raise
    
    async def _create_cloud_configs(self, deployment_dir: Path):
        """Create cloud deployment templates"""
        try:
            cloud_dir = deployment_dir / "cloud"
            cloud_dir.mkdir(exist_ok=True)
            
            # AWS CloudFormation template
            aws_template = {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Description": "Enterprise MCP Platform on AWS",
                "Parameters": {
                    "InstanceType": {
                        "Type": "String",
                        "Default": "t3.large",
                        "Description": "EC2 instance type"
                    }
                },
                "Resources": {
                    "MCPSecurityGroup": {
                        "Type": "AWS::EC2::SecurityGroup",
                        "Properties": {
                            "GroupDescription": "Security group for Enterprise MCP",
                            "SecurityGroupIngress": [
                                {"IpProtocol": "tcp", "FromPort": 8000, "ToPort": 8002, "CidrIp": "0.0.0.0/0"},
                                {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "CidrIp": "0.0.0.0/0"}
                            ]
                        }
                    },
                    "MCPInstance": {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {
                            "InstanceType": {"Ref": "InstanceType"},
                            "ImageId": "ami-0c02fb55956c7d316",
                            "SecurityGroups": [{"Ref": "MCPSecurityGroup"}],
                            "UserData": {
                                "Fn::Base64": {
                                    "Fn::Join": ["", [
                                        "#!/bin/bash\n",
                                        "yum update -y\n",
                                        "yum install -y docker\n",
                                        "service docker start\n",
                                        "usermod -a -G docker ec2-user\n"
                                    ]]
                                }
                            }
                        }
                    }
                },
                "Outputs": {
                    "DashboardURL": {
                        "Description": "Enterprise MCP Dashboard URL",
                        "Value": {"Fn::Sub": "http://${MCPInstance.PublicDnsName}:8000"}
                    }
                }
            }
            
            with open(cloud_dir / "aws-cloudformation.yaml", 'w') as f:
                yaml.dump(aws_template, f, default_flow_style=False)
            
            # Azure ARM template
            azure_template = {
                "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {
                    "vmSize": {
                        "type": "string",
                        "defaultValue": "Standard_D2s_v3",
                        "metadata": {"description": "Size of the virtual machine"}
                    }
                },
                "resources": [
                    {
                        "type": "Microsoft.Compute/virtualMachines",
                        "apiVersion": "2019-07-01",
                        "name": "enterprise-mcp-vm",
                        "location": "[resourceGroup().location]",
                        "properties": {
                            "hardwareProfile": {"vmSize": "[parameters('vmSize')]"},
                            "storageProfile": {
                                "imageReference": {
                                    "publisher": "Canonical",
                                    "offer": "UbuntuServer", 
                                    "sku": "20.04-LTS",
                                    "version": "latest"
                                }
                            }
                        }
                    }
                ]
            }
            
            with open(cloud_dir / "azure-arm-template.json", 'w') as f:
                json.dump(azure_template, f, indent=2)
            
            self.logger.info("☁️ Cloud deployment templates created")
            
        except Exception as e:
            self.logger.error(f"❌ Cloud configuration creation failed: {str(e)}")
            raise
    
    async def _generate_deployment_docs(self, deployment_dir: Path):
        """Generate deployment documentation"""
        try:
            docs_dir = deployment_dir / "docs"
            docs_dir.mkdir(exist_ok=True)
            
            # Main deployment guide
            deployment_guide = f"""# 🚀 Enterprise MCP Platform Deployment Guide

## Overview
This package contains everything needed to deploy the Enterprise MCP Platform with {len(self.validated_servers)} validated servers and 202 tools.

## Quick Start

### Docker Deployment (Recommended)
```bash
cd docker/
chmod +x deploy.sh
./deploy.sh
```

### Kubernetes Deployment
```bash
kubectl apply -f kubernetes/
```

### Manual Installation
```bash
cd app/
pip install -r requirements.txt
pip install -r requirements_mcp.txt
python -m interfaces.web_dashboard
```

## Configuration

### Environment Variables
- `GITHUB_TOKEN`: GitHub API token
- `POSTMAN_API_KEY`: Postman API key
- `TRELLO_API_KEY`: Trello API key
- `ENCRYPTION_KEY`: Encryption key for secure storage

### Validated Servers
{chr(10).join(f"- {server}" for server in self.validated_servers)}

## Access Points
- **Dashboard**: http://localhost:8000
- **API**: http://localhost:8001/api/docs  
- **Monitoring**: http://localhost:8002

## Security
- Enterprise-grade security enabled
- API key authentication required
- Audit logging active
- TLS encryption supported

## Support
For issues and support, refer to the troubleshooting guide.

Generated: {datetime.now().isoformat()}
Version: {self.deployment_config["version"]}
"""
            
            with open(docs_dir / "DEPLOYMENT_GUIDE.md", 'w') as f:
                f.write(deployment_guide)
            
            # Troubleshooting guide
            troubleshooting = """# 🔧 Troubleshooting Guide

## Common Issues

### Services Not Starting
1. Check Docker/container status
2. Verify port availability (8000-8003)
3. Check logs: `docker-compose logs`

### API Connection Issues
1. Verify API keys are configured
2. Check network connectivity
3. Validate server configurations

### Performance Issues
1. Monitor resource usage
2. Check connection pool settings
3. Review cache configuration

## Health Checks
- Dashboard: `curl http://localhost:8000/api/health`
- API: `curl http://localhost:8001/api/health`

## Log Locations
- Application logs: `/app/logs/`
- System logs: `docker-compose logs`

## Support Resources
- Documentation: `/docs/`
- API Reference: `/api/docs`
- Configuration: `/config/`
"""
            
            with open(docs_dir / "TROUBLESHOOTING.md", 'w') as f:
                f.write(troubleshooting)
            
            self.logger.info("📚 Deployment documentation generated")
            
        except Exception as e:
            self.logger.error(f"❌ Documentation generation failed: {str(e)}")
            raise
    
    async def validate_deployment(self, deployment_dir: str) -> Dict[str, Any]:
        """Validate deployment package"""
        try:
            self.logger.info("🔍 Validating deployment package...")
            
            deployment_path = Path(deployment_dir)
            validation_results = {
                "valid": True,
                "checks": [],
                "errors": [],
                "warnings": []
            }
            
            # Check required directories
            required_dirs = ["app", "config", "docker", "kubernetes", "cloud", "docs"]
            for dir_name in required_dirs:
                if (deployment_path / dir_name).exists():
                    validation_results["checks"].append(f"✅ {dir_name}/ directory exists")
                else:
                    validation_results["errors"].append(f"❌ Missing {dir_name}/ directory")
                    validation_results["valid"] = False
            
            # Check required files
            required_files = [
                "docker/Dockerfile",
                "docker/docker-compose.yml", 
                "kubernetes/deployment.yaml",
                "config/deployment.yaml",
                "docs/DEPLOYMENT_GUIDE.md"
            ]
            
            for file_path in required_files:
                if (deployment_path / file_path).exists():
                    validation_results["checks"].append(f"✅ {file_path} exists")
                else:
                    validation_results["errors"].append(f"❌ Missing {file_path}")
                    validation_results["valid"] = False
            
            # Validate application files
            app_dir = deployment_path / "app"
            if app_dir.exists():
                if (app_dir / "autonomous_mcp").exists():
                    validation_results["checks"].append("✅ Core autonomous_mcp module present")
                else:
                    validation_results["errors"].append("❌ Missing autonomous_mcp module")
                    validation_results["valid"] = False
                
                if (app_dir / "enterprise").exists():
                    validation_results["checks"].append("✅ Enterprise modules present")
                else:
                    validation_results["warnings"].append("⚠️ Enterprise modules missing")
            
            validation_results["summary"] = {
                "total_checks": len(validation_results["checks"]),
                "total_errors": len(validation_results["errors"]),
                "total_warnings": len(validation_results["warnings"]),
                "deployment_ready": validation_results["valid"]
            }
            
            if validation_results["valid"]:
                self.logger.info("✅ Deployment package validation successful")
            else:
                self.logger.error("❌ Deployment package validation failed")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"❌ Deployment validation failed: {str(e)}")
            return {"valid": False, "error": str(e)}

    async def deploy_to_docker(self, deployment_dir: str) -> Dict[str, Any]:
        """Deploy using Docker"""
        try:
            self.logger.info("🐳 Starting Docker deployment...")
            
            docker_dir = Path(deployment_dir) / "docker"
            if not docker_dir.exists():
                raise FileNotFoundError("Docker configuration not found")
            
            # Change to docker directory
            original_cwd = os.getcwd()
            os.chdir(docker_dir)
            
            try:
                # Run deployment script
                result = subprocess.run(
                    ["./deploy.sh"],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    self.logger.info("✅ Docker deployment successful")
                    return {
                        "success": True,
                        "message": "Docker deployment completed",
                        "output": result.stdout,
                        "dashboard_url": "http://localhost:8000",
                        "api_url": "http://localhost:8001/api/docs"
                    }
                else:
                    self.logger.error("❌ Docker deployment failed")
                    return {
                        "success": False,
                        "message": "Docker deployment failed",
                        "error": result.stderr
                    }
                    
            finally:
                os.chdir(original_cwd)
                
        except Exception as e:
            self.logger.error(f"❌ Docker deployment error: {str(e)}")
            return {"success": False, "error": str(e)}

# Deployment management functions
async def create_enterprise_deployment(project_root: str) -> str:
    """Create enterprise deployment package"""
    deployer = AutomatedDeployment(project_root)
    return await deployer.create_deployment_package()

async def validate_enterprise_deployment(deployment_dir: str) -> Dict[str, Any]:
    """Validate enterprise deployment package"""
    deployer = AutomatedDeployment(".")
    return await deployer.validate_deployment(deployment_dir)

async def deploy_enterprise_platform(deployment_dir: str, method: str = "docker") -> Dict[str, Any]:
    """Deploy enterprise platform"""
    deployer = AutomatedDeployment(".")
    
    if method == "docker":
        return await deployer.deploy_to_docker(deployment_dir)
    else:
        return {"success": False, "error": f"Deployment method '{method}' not implemented"}
