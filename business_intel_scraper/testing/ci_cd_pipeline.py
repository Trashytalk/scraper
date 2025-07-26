"""
Automated CI/CD Testing Pipeline
GitHub Actions, test automation, quality gates, and deployment validation
"""

import os
import yaml
import json
import subprocess
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import tempfile
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """CI/CD pipeline configuration"""
    name: str
    triggers: List[str]  # push, pull_request, schedule
    environments: List[str]  # test, staging, production
    test_stages: List[str]  # unit, integration, e2e, security, performance
    quality_gates: Dict[str, Any]
    deployment_strategy: str  # rolling, blue_green, canary
    notification_channels: List[str]


@dataclass
class QualityGate:
    """Quality gate configuration"""
    name: str
    type: str  # test_coverage, security_scan, performance_threshold
    threshold: float
    required: bool = True
    block_deployment: bool = True


@dataclass
class PipelineResult:
    """Pipeline execution result"""
    pipeline_id: str
    status: str  # success, failure, cancelled
    stages: Dict[str, Any]
    duration: float
    artifacts: List[str]
    quality_gates: Dict[str, bool]
    deployment_status: Optional[str] = None


class GitHubActionsGenerator:
    """Generate GitHub Actions workflows"""
    
    def __init__(self):
        self.workflows_dir = ".github/workflows"
    
    def generate_ci_workflow(self, config: PipelineConfig) -> str:
        """Generate CI workflow YAML"""
        
        workflow = {
            'name': config.name,
            'on': self._generate_triggers(config.triggers),
            'env': {
                'NODE_VERSION': '18',
                'PYTHON_VERSION': '3.12',
                'POSTGRES_VERSION': '15'
            },
            'jobs': {
                'test': self._generate_test_job(config),
                'security': self._generate_security_job(config),
                'build': self._generate_build_job(config)
            }
        }
        
        # Add deployment jobs if configured
        if 'staging' in config.environments:
            workflow['jobs']['deploy-staging'] = self._generate_deploy_job('staging', config)
        
        if 'production' in config.environments:
            workflow['jobs']['deploy-production'] = self._generate_deploy_job('production', config)
        
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)
    
    def _generate_triggers(self, triggers: List[str]) -> Dict[str, Any]:
        """Generate workflow triggers"""
        trigger_config = {}
        
        if 'push' in triggers:
            trigger_config['push'] = {
                'branches': ['main', 'develop'],
                'paths-ignore': ['docs/**', '*.md']
            }
        
        if 'pull_request' in triggers:
            trigger_config['pull_request'] = {
                'branches': ['main', 'develop'],
                'types': ['opened', 'synchronize', 'reopened']
            }
        
        if 'schedule' in triggers:
            trigger_config['schedule'] = [
                {'cron': '0 2 * * *'}  # Daily at 2 AM
            ]
        
        return trigger_config
    
    def _generate_test_job(self, config: PipelineConfig) -> Dict[str, Any]:
        """Generate test job configuration"""
        
        steps = [
            {
                'name': 'Checkout code',
                'uses': 'actions/checkout@v4'
            },
            {
                'name': 'Setup Python',
                'uses': 'actions/setup-python@v4',
                'with': {
                    'python-version': '${{ env.PYTHON_VERSION }}'
                }
            },
            {
                'name': 'Setup Node.js',
                'uses': 'actions/setup-node@v4',
                'with': {
                    'node-version': '${{ env.NODE_VERSION }}',
                    'cache': 'npm'
                }
            },
            {
                'name': 'Install Python dependencies',
                'run': '''
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                pip install -r requirements-test.txt
                '''
            },
            {
                'name': 'Install Node.js dependencies',
                'run': 'npm ci',
                'working-directory': './frontend'
            }
        ]
        
        # Add test steps based on configuration
        if 'unit' in config.test_stages:
            steps.extend([
                {
                    'name': 'Run unit tests',
                    'run': '''
                    python -m pytest tests/unit/ \
                      --cov=business_intel_scraper \
                      --cov-report=xml \
                      --cov-report=html \
                      --junit-xml=test-results/unit-tests.xml
                    '''
                },
                {
                    'name': 'Frontend unit tests',
                    'run': 'npm run test:unit',
                    'working-directory': './frontend'
                }
            ])
        
        if 'integration' in config.test_stages:
            steps.extend([
                {
                    'name': 'Start test services',
                    'run': '''
                    docker-compose -f docker-compose.test.yml up -d
                    sleep 30
                    '''
                },
                {
                    'name': 'Run integration tests',
                    'run': '''
                    python -m pytest tests/integration/ \
                      --junit-xml=test-results/integration-tests.xml
                    '''
                },
                {
                    'name': 'Stop test services',
                    'run': 'docker-compose -f docker-compose.test.yml down',
                    'if': 'always()'
                }
            ])
        
        if 'e2e' in config.test_stages:
            steps.extend([
                {
                    'name': 'Start application',
                    'run': '''
                    docker-compose up -d
                    sleep 60
                    '''
                },
                {
                    'name': 'Run E2E tests',
                    'run': '''
                    python -m pytest tests/e2e/ \
                      --junit-xml=test-results/e2e-tests.xml
                    '''
                },
                {
                    'name': 'Stop application',
                    'run': 'docker-compose down',
                    'if': 'always()'
                }
            ])
        
        # Upload test results
        steps.extend([
            {
                'name': 'Upload test results',
                'uses': 'actions/upload-artifact@v3',
                'if': 'always()',
                'with': {
                    'name': 'test-results',
                    'path': 'test-results/'
                }
            },
            {
                'name': 'Upload coverage reports',
                'uses': 'codecov/codecov-action@v3',
                'if': 'always()',
                'with': {
                    'file': './coverage.xml',
                    'flags': 'unittests',
                    'name': 'codecov-umbrella'
                }
            }
        ])
        
        return {
            'runs-on': 'ubuntu-latest',
            'services': {
                'postgres': {
                    'image': 'postgres:${{ env.POSTGRES_VERSION }}',
                    'env': {
                        'POSTGRES_PASSWORD': 'testpass',
                        'POSTGRES_DB': 'testdb'
                    },
                    'options': '--health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5',
                    'ports': ['5432:5432']
                },
                'redis': {
                    'image': 'redis:7',
                    'options': '--health-cmd "redis-cli ping" --health-interval 10s --health-timeout 5s --health-retries 5',
                    'ports': ['6379:6379']
                }
            },
            'steps': steps
        }
    
    def _generate_security_job(self, config: PipelineConfig) -> Dict[str, Any]:
        """Generate security scanning job"""
        
        steps = [
            {
                'name': 'Checkout code',
                'uses': 'actions/checkout@v4'
            },
            {
                'name': 'Run Bandit security scan',
                'run': '''
                pip install bandit[toml]
                bandit -r business_intel_scraper/ -f json -o security-report.json
                '''
            },
            {
                'name': 'Run Safety dependency scan',
                'run': '''
                pip install safety
                safety check --json --output safety-report.json
                '''
            },
            {
                'name': 'Run Semgrep security scan',
                'uses': 'returntocorp/semgrep-action@v1',
                'with': {
                    'config': 'auto'
                }
            },
            {
                'name': 'Frontend security audit',
                'run': 'npm audit --audit-level=high',
                'working-directory': './frontend'
            },
            {
                'name': 'Upload security reports',
                'uses': 'actions/upload-artifact@v3',
                'if': 'always()',
                'with': {
                    'name': 'security-reports',
                    'path': '*-report.json'
                }
            }
        ]
        
        return {
            'runs-on': 'ubuntu-latest',
            'needs': ['test'],
            'steps': steps
        }
    
    def _generate_build_job(self, config: PipelineConfig) -> Dict[str, Any]:
        """Generate build job configuration"""
        
        steps = [
            {
                'name': 'Checkout code',
                'uses': 'actions/checkout@v4'
            },
            {
                'name': 'Setup Docker Buildx',
                'uses': 'docker/setup-buildx-action@v3'
            },
            {
                'name': 'Login to Docker Hub',
                'uses': 'docker/login-action@v3',
                'with': {
                    'username': '${{ secrets.DOCKER_USERNAME }}',
                    'password': '${{ secrets.DOCKER_PASSWORD }}'
                }
            },
            {
                'name': 'Build and push Docker images',
                'uses': 'docker/build-push-action@v5',
                'with': {
                    'context': '.',
                    'file': './Dockerfile',
                    'push': True,
                    'tags': '''
                    business-intel-scraper:latest
                    business-intel-scraper:${{ github.sha }}
                    ''',
                    'cache-from': 'type=gha',
                    'cache-to': 'type=gha,mode=max'
                }
            },
            {
                'name': 'Build frontend',
                'run': '''
                npm ci
                npm run build
                ''',
                'working-directory': './frontend'
            },
            {
                'name': 'Upload build artifacts',
                'uses': 'actions/upload-artifact@v3',
                'with': {
                    'name': 'build-artifacts',
                    'path': '''
                    frontend/dist/
                    docker-compose.yml
                    '''
                }
            }
        ]
        
        return {
            'runs-on': 'ubuntu-latest',
            'needs': ['test', 'security'],
            'steps': steps
        }
    
    def _generate_deploy_job(self, environment: str, config: PipelineConfig) -> Dict[str, Any]:
        """Generate deployment job"""
        
        needs = ['build']
        if environment == 'production':
            needs = ['deploy-staging']
        
        steps = [
            {
                'name': 'Checkout code',
                'uses': 'actions/checkout@v4'
            },
            {
                'name': 'Download build artifacts',
                'uses': 'actions/download-artifact@v3',
                'with': {
                    'name': 'build-artifacts'
                }
            }
        ]
        
        # Add environment-specific deployment steps
        if config.deployment_strategy == 'rolling':
            steps.extend(self._generate_rolling_deploy_steps(environment))
        elif config.deployment_strategy == 'blue_green':
            steps.extend(self._generate_blue_green_deploy_steps(environment))
        elif config.deployment_strategy == 'canary':
            steps.extend(self._generate_canary_deploy_steps(environment))
        
        # Add post-deployment validation
        steps.extend([
            {
                'name': 'Run health checks',
                'run': '''
                python scripts/health_check.py --environment ${{ matrix.environment }}
                '''
            },
            {
                'name': 'Run smoke tests',
                'run': '''
                python -m pytest tests/smoke/ --environment ${{ matrix.environment }}
                '''
            }
        ])
        
        return {
            'runs-on': 'ubuntu-latest',
            'needs': needs,
            'environment': environment,
            'if': f"github.ref == 'refs/heads/main' && github.event_name == 'push'" if environment == 'production' else None,
            'strategy': {
                'matrix': {
                    'environment': [environment]
                }
            },
            'steps': steps
        }
    
    def _generate_rolling_deploy_steps(self, environment: str) -> List[Dict[str, Any]]:
        """Generate rolling deployment steps"""
        return [
            {
                'name': 'Deploy to Kubernetes',
                'run': f'''
                kubectl config use-context {environment}
                kubectl set image deployment/business-intel-scraper \\
                  business-intel-scraper=business-intel-scraper:${{{{ github.sha }}}}
                kubectl rollout status deployment/business-intel-scraper --timeout=600s
                '''
            }
        ]
    
    def _generate_blue_green_deploy_steps(self, environment: str) -> List[Dict[str, Any]]:
        """Generate blue-green deployment steps"""
        return [
            {
                'name': 'Deploy to green environment',
                'run': f'''
                kubectl config use-context {environment}
                kubectl apply -f k8s/green-deployment.yml
                kubectl wait --for=condition=available --timeout=600s deployment/business-intel-scraper-green
                '''
            },
            {
                'name': 'Switch traffic to green',
                'run': '''
                kubectl patch service business-intel-scraper -p '{"spec":{"selector":{"version":"green"}}}'
                '''
            },
            {
                'name': 'Scale down blue environment',
                'run': '''
                kubectl scale deployment business-intel-scraper-blue --replicas=0
                '''
            }
        ]
    
    def _generate_canary_deploy_steps(self, environment: str) -> List[Dict[str, Any]]:
        """Generate canary deployment steps"""
        return [
            {
                'name': 'Deploy canary version',
                'run': f'''
                kubectl config use-context {environment}
                kubectl apply -f k8s/canary-deployment.yml
                kubectl wait --for=condition=available --timeout=600s deployment/business-intel-scraper-canary
                '''
            },
            {
                'name': 'Configure traffic split (10% canary)',
                'run': '''
                kubectl apply -f k8s/traffic-split-10.yml
                sleep 300  # Monitor for 5 minutes
                '''
            },
            {
                'name': 'Increase canary traffic (50%)',
                'run': '''
                kubectl apply -f k8s/traffic-split-50.yml
                sleep 300  # Monitor for 5 minutes
                '''
            },
            {
                'name': 'Full canary rollout (100%)',
                'run': '''
                kubectl apply -f k8s/traffic-split-100.yml
                kubectl scale deployment business-intel-scraper-stable --replicas=0
                '''
            }
        ]
    
    def save_workflow(self, workflow_yaml: str, filename: str):
        """Save workflow to file"""
        os.makedirs(self.workflows_dir, exist_ok=True)
        
        with open(os.path.join(self.workflows_dir, filename), 'w') as f:
            f.write(workflow_yaml)
        
        logger.info(f"Workflow saved to {self.workflows_dir}/{filename}")


class QualityGateManager:
    """Manage quality gates and validation"""
    
    def __init__(self, config: Dict[str, QualityGate]):
        self.quality_gates = config
        self.results = {}
    
    def evaluate_quality_gates(self, test_results: Dict[str, Any], 
                             metrics: Dict[str, float]) -> Dict[str, bool]:
        """Evaluate all quality gates"""
        results = {}
        
        for gate_name, gate in self.quality_gates.items():
            result = self._evaluate_gate(gate, test_results, metrics)
            results[gate_name] = result
            
            if gate.required and not result:
                logger.error(f"Required quality gate failed: {gate_name}")
            
        return results
    
    def _evaluate_gate(self, gate: QualityGate, test_results: Dict[str, Any], 
                      metrics: Dict[str, float]) -> bool:
        """Evaluate individual quality gate"""
        
        if gate.type == 'test_coverage':
            coverage = metrics.get('test_coverage', 0)
            return coverage >= gate.threshold
        
        elif gate.type == 'test_pass_rate':
            total_tests = metrics.get('total_tests', 0)
            passed_tests = metrics.get('passed_tests', 0)
            pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            return pass_rate >= gate.threshold
        
        elif gate.type == 'security_vulnerabilities':
            vulnerabilities = metrics.get('security_vulnerabilities', float('inf'))
            return vulnerabilities <= gate.threshold
        
        elif gate.type == 'performance_response_time':
            response_time = metrics.get('avg_response_time', float('inf'))
            return response_time <= gate.threshold
        
        elif gate.type == 'performance_error_rate':
            error_rate = metrics.get('error_rate', 100)
            return error_rate <= gate.threshold
        
        elif gate.type == 'code_quality_score':
            quality_score = metrics.get('code_quality_score', 0)
            return quality_score >= gate.threshold
        
        else:
            logger.warning(f"Unknown quality gate type: {gate.type}")
            return True
    
    def should_block_deployment(self, gate_results: Dict[str, bool]) -> bool:
        """Check if deployment should be blocked"""
        for gate_name, passed in gate_results.items():
            gate = self.quality_gates[gate_name]
            if gate.block_deployment and not passed:
                return True
        return False


class TestMetricsCollector:
    """Collect and analyze test metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    def collect_test_metrics(self, test_results: Dict[str, Any]) -> Dict[str, float]:
        """Collect metrics from test results"""
        metrics = {}
        
        # Test execution metrics
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        total_duration = 0
        
        for category, results in test_results.items():
            if isinstance(results, list):
                for result in results:
                    total_tests += 1
                    if result.status == "PASS":
                        passed_tests += 1
                    elif result.status == "FAIL":
                        failed_tests += 1
                    total_duration += result.duration
        
        metrics['total_tests'] = total_tests
        metrics['passed_tests'] = passed_tests
        metrics['failed_tests'] = failed_tests
        metrics['test_pass_rate'] = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        metrics['avg_test_duration'] = total_duration / total_tests if total_tests > 0 else 0
        
        # Performance metrics
        if 'performance' in test_results:
            perf_results = test_results['performance']
            if isinstance(perf_results, dict):
                # Extract performance metrics
                response_times = []
                error_rates = []
                
                for test_name, result in perf_results.items():
                    if 'avg_response_time' in result:
                        response_times.append(result['avg_response_time'])
                    if 'error_rate_percent' in result:
                        error_rates.append(result['error_rate_percent'])
                
                if response_times:
                    metrics['avg_response_time'] = sum(response_times) / len(response_times)
                    metrics['max_response_time'] = max(response_times)
                
                if error_rates:
                    metrics['avg_error_rate'] = sum(error_rates) / len(error_rates)
                    metrics['max_error_rate'] = max(error_rates)
        
        return metrics
    
    def collect_coverage_metrics(self, coverage_file: str = 'coverage.xml') -> Dict[str, float]:
        """Collect code coverage metrics"""
        metrics = {}
        
        try:
            import xml.etree.ElementTree as ET
            
            if os.path.exists(coverage_file):
                tree = ET.parse(coverage_file)
                root = tree.getroot()
                
                # Extract coverage percentage
                coverage_elem = root.find('.//coverage')
                if coverage_elem is not None:
                    line_rate = float(coverage_elem.get('line-rate', 0))
                    branch_rate = float(coverage_elem.get('branch-rate', 0))
                    
                    metrics['line_coverage'] = line_rate * 100
                    metrics['branch_coverage'] = branch_rate * 100
                    metrics['test_coverage'] = (line_rate + branch_rate) / 2 * 100
        
        except Exception as e:
            logger.warning(f"Failed to collect coverage metrics: {e}")
            metrics['test_coverage'] = 0
        
        return metrics
    
    def collect_security_metrics(self, security_reports_dir: str = 'security-reports') -> Dict[str, float]:
        """Collect security scan metrics"""
        metrics = {}
        
        total_vulnerabilities = 0
        high_severity_vulns = 0
        
        try:
            # Process Bandit report
            bandit_file = os.path.join(security_reports_dir, 'bandit-report.json')
            if os.path.exists(bandit_file):
                with open(bandit_file, 'r') as f:
                    bandit_data = json.load(f)
                    
                issues = bandit_data.get('results', [])
                total_vulnerabilities += len(issues)
                
                for issue in issues:
                    if issue.get('issue_severity') in ['HIGH', 'MEDIUM']:
                        high_severity_vulns += 1
            
            # Process Safety report
            safety_file = os.path.join(security_reports_dir, 'safety-report.json')
            if os.path.exists(safety_file):
                with open(safety_file, 'r') as f:
                    safety_data = json.load(f)
                    
                vulnerabilities = safety_data.get('vulnerabilities', [])
                total_vulnerabilities += len(vulnerabilities)
        
        except Exception as e:
            logger.warning(f"Failed to collect security metrics: {e}")
        
        metrics['security_vulnerabilities'] = total_vulnerabilities
        metrics['high_severity_vulnerabilities'] = high_severity_vulns
        
        return metrics


class NotificationManager:
    """Manage pipeline notifications"""
    
    def __init__(self, channels: List[str]):
        self.channels = channels
    
    def send_notification(self, message: str, severity: str = 'info'):
        """Send notification to configured channels"""
        
        for channel in self.channels:
            try:
                if channel == 'slack':
                    self._send_slack_notification(message, severity)
                elif channel == 'email':
                    self._send_email_notification(message, severity)
                elif channel == 'github':
                    self._send_github_notification(message, severity)
            except Exception as e:
                logger.error(f"Failed to send notification to {channel}: {e}")
    
    def _send_slack_notification(self, message: str, severity: str):
        """Send Slack notification"""
        # Implementation would use Slack API
        logger.info(f"Slack notification: {message}")
    
    def _send_email_notification(self, message: str, severity: str):
        """Send email notification"""
        # Implementation would use SMTP
        logger.info(f"Email notification: {message}")
    
    def _send_github_notification(self, message: str, severity: str):
        """Send GitHub notification (issue/comment)"""
        # Implementation would use GitHub API
        logger.info(f"GitHub notification: {message}")


class PipelineOrchestrator:
    """Orchestrate the entire CI/CD pipeline"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.github_actions = GitHubActionsGenerator()
        self.quality_gates = QualityGateManager(config.quality_gates)
        self.metrics_collector = TestMetricsCollector()
        self.notification_manager = NotificationManager(config.notification_channels)
    
    def setup_pipeline(self):
        """Setup CI/CD pipeline"""
        logger.info("Setting up CI/CD pipeline")
        
        # Generate GitHub Actions workflow
        workflow_yaml = self.github_actions.generate_ci_workflow(self.config)
        self.github_actions.save_workflow(workflow_yaml, 'ci-cd.yml')
        
        # Generate additional workflows
        self._generate_additional_workflows()
        
        # Create configuration files
        self._create_config_files()
        
        logger.info("CI/CD pipeline setup complete")
    
    def _generate_additional_workflows(self):
        """Generate additional specialized workflows"""
        
        # Security scanning workflow
        security_workflow = {
            'name': 'Security Scan',
            'on': {
                'schedule': [{'cron': '0 6 * * *'}],  # Daily at 6 AM
                'workflow_dispatch': {}
            },
            'jobs': {
                'security-scan': self.github_actions._generate_security_job(self.config)
            }
        }
        
        security_yaml = yaml.dump(security_workflow, default_flow_style=False)
        self.github_actions.save_workflow(security_yaml, 'security-scan.yml')
        
        # Performance testing workflow
        performance_workflow = {
            'name': 'Performance Testing',
            'on': {
                'schedule': [{'cron': '0 22 * * 0'}],  # Weekly on Sunday at 10 PM
                'workflow_dispatch': {}
            },
            'jobs': {
                'performance-test': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'name': 'Checkout code', 'uses': 'actions/checkout@v4'},
                        {'name': 'Setup Python', 'uses': 'actions/setup-python@v4', 'with': {'python-version': '3.12'}},
                        {'name': 'Install dependencies', 'run': 'pip install -r requirements.txt'},
                        {'name': 'Run performance tests', 'run': 'python -m pytest tests/performance/ --junit-xml=performance-results.xml'},
                        {'name': 'Upload results', 'uses': 'actions/upload-artifact@v3', 'with': {'name': 'performance-results', 'path': 'performance-results.xml'}}
                    ]
                }
            }
        }
        
        performance_yaml = yaml.dump(performance_workflow, default_flow_style=False)
        self.github_actions.save_workflow(performance_yaml, 'performance-testing.yml')
    
    def _create_config_files(self):
        """Create necessary configuration files"""
        
        # pytest configuration
        pytest_config = """
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
    --cov=business_intel_scraper
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    security: Security tests
    slow: Slow running tests
"""
        
        with open('pytest.ini', 'w') as f:
            f.write(pytest_config)
        
        # Docker Compose for testing
        docker_compose_test = """
version: '3.8'

services:
  postgres-test:
    image: postgres:15
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
    ports:
      - "5433:5432"
    volumes:
      - postgres_test_data:/var/lib/postgresql/data

  redis-test:
    image: redis:7-alpine
    ports:
      - "6380:6379"

  app-test:
    build: .
    environment:
      DATABASE_URL: postgresql://testuser:testpass@postgres-test:5432/testdb
      REDIS_URL: redis://redis-test:6379
      ENVIRONMENT: test
    depends_on:
      - postgres-test
      - redis-test
    ports:
      - "8001:8000"

volumes:
  postgres_test_data:
"""
        
        with open('docker-compose.test.yml', 'w') as f:
            f.write(docker_compose_test)


# Example usage and configuration
def create_example_pipeline():
    """Create example CI/CD pipeline configuration"""
    
    # Define quality gates
    quality_gates = {
        'test_coverage': QualityGate(
            name='Test Coverage',
            type='test_coverage',
            threshold=80.0,
            required=True,
            block_deployment=True
        ),
        'test_pass_rate': QualityGate(
            name='Test Pass Rate', 
            type='test_pass_rate',
            threshold=95.0,
            required=True,
            block_deployment=True
        ),
        'security_scan': QualityGate(
            name='Security Vulnerabilities',
            type='security_vulnerabilities',
            threshold=0.0,
            required=True,
            block_deployment=True
        ),
        'performance_response_time': QualityGate(
            name='Response Time',
            type='performance_response_time',
            threshold=2.0,  # 2 seconds
            required=False,
            block_deployment=False
        ),
        'performance_error_rate': QualityGate(
            name='Error Rate',
            type='performance_error_rate', 
            threshold=1.0,  # 1%
            required=True,
            block_deployment=True
        )
    }
    
    # Create pipeline configuration
    pipeline_config = PipelineConfig(
        name='Business Intelligence Scraper CI/CD',
        triggers=['push', 'pull_request', 'schedule'],
        environments=['test', 'staging', 'production'],
        test_stages=['unit', 'integration', 'e2e', 'security', 'performance'],
        quality_gates=quality_gates,
        deployment_strategy='blue_green',
        notification_channels=['slack', 'github']
    )
    
    return pipeline_config


if __name__ == "__main__":
    # Setup CI/CD pipeline
    config = create_example_pipeline()
    orchestrator = PipelineOrchestrator(config)
    orchestrator.setup_pipeline()
    
    logger.info("CI/CD pipeline setup completed successfully!")
    logger.info("Generated files:")
    logger.info("- .github/workflows/ci-cd.yml")
    logger.info("- .github/workflows/security-scan.yml")
    logger.info("- .github/workflows/performance-testing.yml")
    logger.info("- pytest.ini")
    logger.info("- docker-compose.test.yml")
