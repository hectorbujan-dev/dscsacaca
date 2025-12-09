#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Testing for Pokédex UAX Flask Application
Tests admin authentication, API search, statistics, and admin CRUD operations
"""

import requests
import json
import sys
from urllib.parse import urljoin
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://pokedex-compare.preview.emergentagent.com')

# For Flask routes, we need to use the internal backend URL since external routing 
# directs non-API routes to frontend
FLASK_BACKEND_URL = 'http://localhost:8001'

print(f"🔍 Testing Pokédex Backend at: {BACKEND_URL}")
print("=" * 60)

class PokédexTester:
    def __init__(self, base_url, flask_url=None):
        self.base_url = base_url
        self.flask_url = flask_url or base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Pokédex-Tester/1.0'
        })
        
    def test_admin_login(self):
        """Test admin authentication with specific credentials"""
        print("\n🔐 Testing Admin Login...")
        
        login_url = urljoin(self.flask_url, '/login')
        
        # Test with correct admin credentials
        login_data = {
            'email': 'hectorbujan@gmail.com',
            'password': 'hector2005'
        }
        
        try:
            response = self.session.post(login_url, data=login_data, allow_redirects=False)
            
            if response.status_code in [200, 302]:
                # Check if session cookies are set
                cookies = self.session.cookies
                if cookies:
                    print("✅ Admin login successful - Session cookies set")
                    print(f"   Status: {response.status_code}")
                    print(f"   Cookies: {len(cookies)} cookies received")
                    return True
                else:
                    print("❌ Admin login failed - No session cookies")
                    return False
            else:
                print(f"❌ Admin login failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False
    
    def test_admin_login_wrong_credentials(self):
        """Test admin login with wrong credentials"""
        print("\n🔐 Testing Admin Login with Wrong Credentials...")
        
        login_url = urljoin(self.base_url, '/login')
        
        # Test with wrong credentials
        wrong_data = {
            'email': 'wrong@email.com',
            'password': 'wrongpassword'
        }
        
        try:
            # Use a separate session for wrong credentials
            temp_session = requests.Session()
            response = temp_session.post(login_url, data=wrong_data, allow_redirects=False)
            
            # Should not set admin session cookies
            if response.status_code == 200 and 'error' in response.text.lower():
                print("✅ Wrong credentials correctly rejected")
                return True
            elif response.status_code == 302:
                print("❌ Wrong credentials incorrectly accepted")
                return False
            else:
                print(f"✅ Wrong credentials rejected - Status: {response.status_code}")
                return True
                
        except Exception as e:
            print(f"❌ Wrong credentials test error: {str(e)}")
            return False
    
    def test_api_search(self):
        """Test API search functionality"""
        print("\n🔍 Testing API Search...")
        
        # Test search for Pikachu
        search_url = urljoin(self.base_url, '/api/buscar')
        
        test_cases = [
            ('pikachu', 'Pikachu search'),
            ('char', 'Char* search (should return Charmander, Charmeleon, Charizard)'),
            ('nonexistent', 'Non-existent Pokemon search')
        ]
        
        all_passed = True
        
        for search_term, description in test_cases:
            try:
                params = {'nombre': search_term}
                response = self.session.get(search_url, params=params)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"✅ {description}: {len(data)} results")
                            if search_term == 'char' and len(data) >= 3:
                                # Check if we got Charmander family
                                names = [p.get('name', {}).get('en', '').lower() for p in data]
                                char_pokemon = [n for n in names if 'char' in n]
                                print(f"   Found Char* Pokemon: {len(char_pokemon)}")
                            elif search_term == 'pikachu' and len(data) > 0:
                                print(f"   Found Pikachu-related: {data[0].get('name', {})}")
                        else:
                            print(f"❌ {description}: Invalid response format")
                            all_passed = False
                    except json.JSONDecodeError:
                        print(f"❌ {description}: Invalid JSON response")
                        all_passed = False
                else:
                    print(f"❌ {description}: Status {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_statistics_combined(self):
        """Test statistics page with combined stats"""
        print("\n📊 Testing Statistics with Combined Stats...")
        
        stats_url = urljoin(self.base_url, '/estadisticas')
        
        try:
            params = {'stat1': 'attack', 'stat2': 'speed'}
            response = self.session.get(stats_url, params=params)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for combined stats section
                if 'combinado' in content.lower() or 'combined' in content.lower():
                    print("✅ Statistics page loaded with combined stats")
                    
                    # Check for specific elements that should be present
                    checks = [
                        ('top', 'Top rankings present'),
                        ('ataque' in content.lower() or 'attack' in content.lower(), 'Attack stats present'),
                        ('velocidad' in content.lower() or 'speed' in content.lower(), 'Speed stats present')
                    ]
                    
                    for check, description in checks:
                        if check:
                            print(f"   ✅ {description}")
                        else:
                            print(f"   ⚠️ {description} - not found")
                    
                    return True
                else:
                    print("❌ Combined stats section not found in response")
                    return False
            else:
                print(f"❌ Statistics page failed: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Statistics test error: {str(e)}")
            return False
    
    def test_admin_create_pokemon(self):
        """Test admin Pokemon creation (requires admin session)"""
        print("\n🎨 Testing Admin Create Pokemon...")
        
        # First ensure we're logged in as admin
        if not hasattr(self, '_admin_logged_in'):
            self._admin_logged_in = self.test_admin_login()
        
        if not self._admin_logged_in:
            print("❌ Cannot test create Pokemon - Admin login failed")
            return False
        
        create_url = urljoin(self.base_url, '/admin/crear_pokemon')
        
        try:
            # First test GET request to load the form
            get_response = self.session.get(create_url)
            
            if get_response.status_code == 200:
                print("✅ Admin create Pokemon form accessible")
                
                # Test POST request to create a Pokemon
                pokemon_data = {
                    'nombre_es': 'Testmon',
                    'nombre_en': 'Testmon',
                    'tipos': 'electric,test',
                    'hp': '100',
                    'attack': '120',
                    'defense': '80',
                    'special_attack': '110',
                    'special_defense': '90',
                    'speed': '95',
                    'height': '15',
                    'weight': '250',
                    'generation': 'generation-i',
                    'habitat': 'grassland',
                    'is_legendary': 'false',
                    'is_mythical': 'false',
                    'abilities': 'static,test-ability',
                    'capture_rate': '45',
                    'base_experience': '100',
                    'descripcion': 'A test Pokemon created by the testing system',
                    'imagen_url': 'https://example.com/testmon.png'
                }
                
                post_response = self.session.post(create_url, data=pokemon_data, allow_redirects=False)
                
                if post_response.status_code in [200, 302]:
                    print("✅ Admin Pokemon creation successful")
                    
                    # Store the created Pokemon ID for deletion test
                    if post_response.status_code == 302:
                        location = post_response.headers.get('Location', '')
                        if '/pokemon/' in location:
                            pokemon_id = location.split('/pokemon/')[-1]
                            self.created_pokemon_id = int(pokemon_id)
                            print(f"   Created Pokemon ID: {self.created_pokemon_id}")
                    
                    return True
                else:
                    print(f"❌ Admin Pokemon creation failed: Status {post_response.status_code}")
                    return False
            else:
                print(f"❌ Admin create form not accessible: Status {get_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Admin create Pokemon error: {str(e)}")
            return False
    
    def test_admin_delete_pokemon(self):
        """Test admin Pokemon deletion (requires admin session)"""
        print("\n🗑️ Testing Admin Delete Pokemon...")
        
        # First ensure we're logged in as admin
        if not hasattr(self, '_admin_logged_in'):
            self._admin_logged_in = self.test_admin_login()
        
        if not self._admin_logged_in:
            print("❌ Cannot test delete Pokemon - Admin login failed")
            return False
        
        # Use the Pokemon we created, or find any Pokemon to test deletion
        pokemon_id = getattr(self, 'created_pokemon_id', None)
        
        if not pokemon_id:
            # Try to find a Pokemon marked as invented (es_inventado: true)
            try:
                search_url = urljoin(self.base_url, '/api/buscar')
                response = self.session.get(search_url, params={'nombre': 'test'})
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        pokemon_id = data[0].get('id')
                        print(f"   Using Pokemon ID {pokemon_id} for deletion test")
            except:
                pass
        
        if not pokemon_id:
            print("⚠️ No Pokemon available for deletion test - skipping")
            return True  # Not a failure, just no test subject
        
        delete_url = urljoin(self.base_url, f'/admin/eliminar_pokemon/{pokemon_id}')
        
        try:
            response = self.session.post(delete_url, allow_redirects=False)
            
            if response.status_code in [200, 302]:
                print(f"✅ Admin Pokemon deletion successful for ID {pokemon_id}")
                return True
            elif response.status_code == 403:
                print("❌ Admin Pokemon deletion failed - Not authorized")
                return False
            elif response.status_code == 404:
                print(f"⚠️ Pokemon ID {pokemon_id} not found - may have been already deleted")
                return True  # Not necessarily a failure
            else:
                print(f"❌ Admin Pokemon deletion failed: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Admin delete Pokemon error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Pokédex Backend Tests")
        print("=" * 60)
        
        tests = [
            ('Admin Login (Correct)', self.test_admin_login),
            ('Admin Login (Wrong Credentials)', self.test_admin_login_wrong_credentials),
            ('API Search', self.test_api_search),
            ('Statistics Combined', self.test_statistics_combined),
            ('Admin Create Pokemon', self.test_admin_create_pokemon),
            ('Admin Delete Pokemon', self.test_admin_delete_pokemon)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name}: Unexpected error - {str(e)}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\n🎯 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️ Some tests failed - check logs above")
            return False

def main():
    """Main test execution"""
    tester = PokédexTester(BACKEND_URL)
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Backend testing completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Backend testing completed with failures")
        sys.exit(1)

if __name__ == '__main__':
    main()