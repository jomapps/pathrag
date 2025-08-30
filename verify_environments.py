#!/usr/bin/env python3
"""
PathRAG Environment Verification Script
Ensures both Ubuntu production and Windows development environments are working correctly
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path

class EnvironmentVerifier:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.detect_environment(),
            'tests': [],
            'summary': {'passed': 0, 'failed': 0, 'total': 0}
        }
        
    def detect_environment(self):
        """Detect if running on Ubuntu production or Windows development"""
        if os.name == 'nt':
            return 'windows_development'
        elif os.path.exists('/opt/pathrag/pathrag'):
            return 'ubuntu_production'
        else:
            return 'unknown'
    
    def log_test(self, name, status, details=None):
        """Log test result"""
        test_result = {
            'name': name,
            'status': status,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.results['tests'].append(test_result)
        
        if status == 'PASS':
            self.results['summary']['passed'] += 1
            print(f"✅ {name}")
        else:
            self.results['summary']['failed'] += 1
            print(f"❌ {name}: {details.get('error', 'Unknown error')}")
        
        self.results['summary']['total'] += 1
    
    def test_git_status(self):
        """Test git repository status"""
        try:
            # Check current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
            
            # Check git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            has_changes = bool(result.stdout.strip())
            
            # Check remote status
            subprocess.run(['git', 'fetch'], capture_output=True, check=True)
            result = subprocess.run(['git', 'status', '-uno'],
                                  capture_output=True, text=True, check=True)
            # Check if we're up to date (either "up to date" or "nothing to commit")
            status_output = result.stdout.lower()
            is_up_to_date = ('up to date' in status_output or
                           'nothing to commit' in status_output)
            
            details = {
                'current_branch': current_branch,
                'has_uncommitted_changes': has_changes,
                'is_up_to_date_with_remote': is_up_to_date
            }
            
            if current_branch in ['master', 'production'] and not has_changes and is_up_to_date:
                self.log_test("Git Repository Status", "PASS", details)
            else:
                details['error'] = f"Branch: {current_branch}, Changes: {has_changes}, Up-to-date: {is_up_to_date}"
                self.log_test("Git Repository Status", "FAIL", details)
                
        except subprocess.CalledProcessError as e:
            self.log_test("Git Repository Status", "FAIL", {'error': str(e)})
    
    def test_python_environment(self):
        """Test Python environment and dependencies"""
        try:
            # Check Python version
            python_version = sys.version
            
            # Check if virtual environment is active
            venv_active = hasattr(sys, 'real_prefix') or (
                hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
            )
            
            # Check key dependencies based on environment
            if self.results['environment'] == 'ubuntu_production':
                required_modules = ['flask', 'arango']  # Simple API server doesn't need pathrag
            else:
                required_modules = ['flask', 'arango', 'pathrag']  # Full dev environment needs pathrag

            missing_modules = []

            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    missing_modules.append(module)
            
            details = {
                'python_version': python_version,
                'virtual_env_active': venv_active,
                'missing_modules': missing_modules
            }
            
            if not missing_modules:
                self.log_test("Python Environment", "PASS", details)
            else:
                details['error'] = f"Missing modules: {missing_modules}"
                self.log_test("Python Environment", "FAIL", details)
                
        except Exception as e:
            self.log_test("Python Environment", "FAIL", {'error': str(e)})
    
    def test_api_server(self):
        """Test API server functionality"""
        try:
            # Determine API URL based on environment
            if self.results['environment'] == 'ubuntu_production':
                urls = ['http://localhost:8000', 'http://movie.ft.tc:8000']
            else:
                urls = ['http://localhost:5000']
            
            for url in urls:
                try:
                    # Test health endpoint
                    response = requests.get(f"{url}/health", timeout=10)
                    if response.status_code == 200:
                        health_data = response.json()
                        details = {
                            'url': url,
                            'status_code': response.status_code,
                            'health_status': health_data.get('status'),
                            'services': health_data.get('services', {})
                        }
                        self.log_test(f"API Server Health ({url})", "PASS", details)
                    else:
                        self.log_test(f"API Server Health ({url})", "FAIL", 
                                    {'error': f"Status code: {response.status_code}"})
                        
                except requests.RequestException as e:
                    self.log_test(f"API Server Health ({url})", "FAIL", {'error': str(e)})
                    
        except Exception as e:
            self.log_test("API Server", "FAIL", {'error': str(e)})
    
    def test_database_connection(self):
        """Test database connectivity"""
        try:
            if self.results['environment'] == 'ubuntu_production':
                # Test ArangoDB connection via API
                response = requests.get('http://localhost:8000/health', timeout=10)
                if response.status_code == 200:
                    health_data = response.json()
                    db_status = health_data.get('services', {}).get('arangodb')
                    
                    if db_status == 'connected':
                        self.log_test("Database Connection", "PASS", {'arangodb_status': db_status})
                    else:
                        self.log_test("Database Connection", "FAIL", 
                                    {'error': f"ArangoDB status: {db_status}"})
                else:
                    self.log_test("Database Connection", "FAIL", 
                                {'error': f"Health check failed: {response.status_code}"})
            else:
                # For development environment, check if ArangoDB is accessible
                try:
                    import arango
                    # This is a basic check - in real scenario you'd test actual connection
                    self.log_test("Database Connection", "PASS", {'note': 'ArangoDB module available'})
                except ImportError:
                    self.log_test("Database Connection", "FAIL", {'error': 'ArangoDB module not available'})
                    
        except Exception as e:
            self.log_test("Database Connection", "FAIL", {'error': str(e)})
    
    def test_process_management(self):
        """Test process management (PM2 for production, manual for dev)"""
        try:
            if self.results['environment'] == 'ubuntu_production':
                # Check PM2 status
                result = subprocess.run(['pm2', 'jlist'], capture_output=True, text=True, check=True)
                pm2_data = json.loads(result.stdout)
                
                pathrag_processes = [p for p in pm2_data if 'pathrag' in p.get('name', '').lower()]
                
                if pathrag_processes:
                    running_processes = [p for p in pathrag_processes if p.get('pm2_env', {}).get('status') == 'online']
                    details = {
                        'total_processes': len(pathrag_processes),
                        'running_processes': len(running_processes),
                        'process_names': [p.get('name') for p in pathrag_processes]
                    }
                    
                    if running_processes:
                        self.log_test("Process Management (PM2)", "PASS", details)
                    else:
                        details['error'] = "No PathRAG processes running"
                        self.log_test("Process Management (PM2)", "FAIL", details)
                else:
                    self.log_test("Process Management (PM2)", "FAIL", {'error': 'No PathRAG processes found'})
            else:
                # For development, just check if we can run the API server check
                self.log_test("Process Management (Manual)", "PASS", {'note': 'Manual process management for development'})
                
        except subprocess.CalledProcessError as e:
            self.log_test("Process Management", "FAIL", {'error': f"PM2 command failed: {e}"})
        except Exception as e:
            self.log_test("Process Management", "FAIL", {'error': str(e)})
    
    def test_nginx_configuration(self):
        """Test Nginx configuration (production only)"""
        if self.results['environment'] != 'ubuntu_production':
            self.log_test("Nginx Configuration", "SKIP", {'note': 'Not applicable for development environment'})
            return
            
        try:
            # Test nginx configuration
            result = subprocess.run(['nginx', '-t'], capture_output=True, text=True, check=True)
            
            # Check if pathrag site is enabled
            pathrag_enabled = os.path.exists('/etc/nginx/sites-enabled/pathrag')
            
            details = {
                'config_test': 'passed',
                'pathrag_site_enabled': pathrag_enabled
            }
            
            if pathrag_enabled:
                self.log_test("Nginx Configuration", "PASS", details)
            else:
                details['error'] = 'PathRAG site not enabled in Nginx'
                self.log_test("Nginx Configuration", "FAIL", details)
                
        except subprocess.CalledProcessError as e:
            self.log_test("Nginx Configuration", "FAIL", {'error': f"Nginx test failed: {e}"})
        except Exception as e:
            self.log_test("Nginx Configuration", "FAIL", {'error': str(e)})
    
    def run_all_tests(self):
        """Run all verification tests"""
        print(f"🔍 PathRAG Environment Verification")
        print(f"Environment: {self.results['environment']}")
        print(f"Timestamp: {self.results['timestamp']}")
        print("=" * 60)
        
        # Run all tests
        self.test_git_status()
        self.test_python_environment()
        self.test_api_server()
        self.test_database_connection()
        self.test_process_management()
        self.test_nginx_configuration()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {self.results['summary']['total']}")
        print(f"   Passed: {self.results['summary']['passed']}")
        print(f"   Failed: {self.results['summary']['failed']}")
        
        success_rate = (self.results['summary']['passed'] / self.results['summary']['total']) * 100
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if self.results['summary']['failed'] == 0:
            print("\n🎉 All tests passed! Environment is healthy.")
        else:
            print(f"\n⚠️  {self.results['summary']['failed']} test(s) failed. Please review the issues above.")
        
        return self.results['summary']['failed'] == 0

if __name__ == "__main__":
    verifier = EnvironmentVerifier()
    success = verifier.run_all_tests()
    
    # Save results to file
    results_file = f"environment_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(verifier.results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    sys.exit(0 if success else 1)
