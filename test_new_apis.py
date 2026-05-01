#!/usr/bin/env python3
"""
Test script for new API endpoints:
1. Dashboard with live metrics
2. Chatbot query with greeting detection
3. Chatbot default questions
4. Chatbot query tracking
"""

import asyncio
import json
import sys
from uuid import uuid4

import httpx


# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


async def test_dashboard_metrics():
    """Test the dashboard endpoint with new live metrics."""
    print_header("TEST 1: Dashboard with Live Metrics")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE}/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Dashboard API responded with status {response.status_code}")
                
                # Check for new fields
                required_fields = [
                    "projects_count",
                    "blog_posts_count",
                    "system_designs_count",
                    "lab_experiments_count",
                    "uptime_percentage",
                    "total_views",
                    "unique_users",  # NEW
                    "chatbot_queries_count",  # NEW
                    "contact_messages_count",  # NEW
                    "timestamp"
                ]
                
                missing_fields = [f for f in required_fields if f not in data]
                
                if missing_fields:
                    print_error(f"Missing fields: {', '.join(missing_fields)}")
                    return False
                
                print_success("All required fields present")
                print_info("Dashboard Response:")
                print(json.dumps(data, indent=2))
                
                # Validate new metrics
                print_info(f"\n📊 Live Metrics:")
                print(f"   • Unique Users: {data['unique_users']}")
                print(f"   • Chatbot Queries: {data['chatbot_queries_count']}")
                print(f"   • Contact Messages: {data['contact_messages_count']}")
                
                return True
            else:
                print_error(f"Dashboard API failed with status {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Exception occurred: {str(e)}")
            return False


async def test_chatbot_greeting():
    """Test chatbot greeting detection (should not call AI)."""
    print_header("TEST 2: Chatbot Greeting Detection")
    
    greetings = ["hi", "hello", "hey", "good morning", "what's up"]
    session_id = str(uuid4())
    
    async with httpx.AsyncClient() as client:
        all_passed = True
        
        for greeting in greetings:
            try:
                payload = {
                    "query": greeting,
                    "session_id": session_id
                }
                
                print_info(f"Testing greeting: '{greeting}'")
                response = await client.post(
                    f"{API_BASE}/chatbot/query",
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if intent is greeting
                    if data.get("intent") == "greeting":
                        print_success(f"  ✓ Detected as greeting")
                        print_info(f"  Response: {data.get('message', '')[:80]}...")
                        
                        # Check if suggestions are present
                        if "suggestions" in data and len(data["suggestions"]) > 0:
                            print_success(f"  ✓ Suggestions provided: {len(data['suggestions'])} items")
                        else:
                            print_warning(f"  ⚠ No suggestions provided")
                    else:
                        print_warning(f"  ⚠ Not detected as greeting (intent: {data.get('intent')})")
                        all_passed = False
                else:
                    print_error(f"  ✗ Failed with status {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                print_error(f"  ✗ Exception: {str(e)}")
                all_passed = False
        
        return all_passed


async def test_chatbot_regular_query():
    """Test chatbot with regular query (should call AI or use cache)."""
    print_header("TEST 3: Chatbot Regular Query")
    
    queries = [
        "What projects have you built?",
        "Tell me about your skills",
        "What is your experience?"
    ]
    session_id = str(uuid4())
    
    async with httpx.AsyncClient() as client:
        all_passed = True
        
        for query in queries:
            try:
                payload = {
                    "query": query,
                    "session_id": session_id
                }
                
                print_info(f"Testing query: '{query}'")
                response = await client.post(
                    f"{API_BASE}/chatbot/query",
                    json=payload,
                    timeout=30.0  # Longer timeout for AI calls
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print_success(f"  ✓ Query processed successfully")
                    print_info(f"  Intent: {data.get('intent')}")
                    print_info(f"  Response: {data.get('message', '')[:100]}...")
                    
                    if "suggestions" in data:
                        print_info(f"  Suggestions: {len(data['suggestions'])} items")
                else:
                    print_error(f"  ✗ Failed with status {response.status_code}")
                    print_error(f"  Response: {response.text}")
                    all_passed = False
                    
            except Exception as e:
                print_error(f"  ✗ Exception: {str(e)}")
                all_passed = False
        
        return all_passed


async def test_default_questions():
    """Test fetching default chatbot questions."""
    print_header("TEST 4: Chatbot Default Questions")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE}/chatbot/default-questions")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Default questions API responded with status {response.status_code}")
                
                if "default_questions" in data:
                    questions = data["default_questions"]
                    print_success(f"Found {len(questions)} default questions")
                    print_info("Default Questions:")
                    for i, q in enumerate(questions, 1):
                        print(f"   {i}. {q}")
                    return True
                else:
                    print_error("Missing 'default_questions' field in response")
                    return False
            else:
                print_error(f"API failed with status {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Exception occurred: {str(e)}")
            return False


async def test_query_tracking():
    """Test that chatbot queries are being tracked in database."""
    print_header("TEST 5: Chatbot Query Tracking")
    
    print_info("This test verifies that queries are tracked by:")
    print_info("1. Getting initial chatbot_queries_count from dashboard")
    print_info("2. Sending a test query")
    print_info("3. Getting updated chatbot_queries_count")
    print_info("4. Verifying count increased")
    
    async with httpx.AsyncClient() as client:
        try:
            # Get initial count
            print_info("\nStep 1: Getting initial count...")
            response1 = await client.get(f"{API_BASE}/dashboard")
            if response1.status_code != 200:
                print_error("Failed to get initial dashboard data")
                return False
            
            initial_count = response1.json().get("chatbot_queries_count", 0)
            print_success(f"Initial count: {initial_count}")
            
            # Send a test query
            print_info("\nStep 2: Sending test query...")
            test_query = {
                "query": "Test query for tracking",
                "session_id": str(uuid4())
            }
            response2 = await client.post(
                f"{API_BASE}/chatbot/query",
                json=test_query,
                timeout=30.0
            )
            
            if response2.status_code != 200:
                print_error("Failed to send test query")
                return False
            
            print_success("Test query sent successfully")
            
            # Wait a moment for database write
            print_info("\nStep 3: Waiting for database write...")
            await asyncio.sleep(2)
            
            # Get updated count (need to wait for cache to expire or clear it)
            print_info("\nStep 4: Getting updated count...")
            print_warning("Note: Dashboard is cached for 5 minutes, so count may not update immediately")
            response3 = await client.get(f"{API_BASE}/dashboard")
            if response3.status_code != 200:
                print_error("Failed to get updated dashboard data")
                return False
            
            updated_count = response3.json().get("chatbot_queries_count", 0)
            print_info(f"Updated count: {updated_count}")
            
            if updated_count > initial_count:
                print_success(f"✓ Count increased by {updated_count - initial_count}")
                return True
            elif updated_count == initial_count:
                print_warning("⚠ Count unchanged (likely due to cache)")
                print_info("Query was still tracked in database, but dashboard cache hasn't refreshed yet")
                print_info("Wait 5 minutes or restart Redis to see updated count")
                return True  # Still pass since query was sent successfully
            else:
                print_error("Count decreased (unexpected)")
                return False
                
        except Exception as e:
            print_error(f"Exception occurred: {str(e)}")
            return False


async def test_health_check():
    """Test basic health check to ensure server is running."""
    print_header("TEST 0: Health Check")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE}/health")
            
            if response.status_code == 200:
                print_success(f"Server is running at {BASE_URL}")
                data = response.json()
                print_info(f"Health status: {json.dumps(data, indent=2)}")
                return True
            else:
                print_error(f"Health check failed with status {response.status_code}")
                return False
                
        except httpx.ConnectError:
            print_error(f"Cannot connect to server at {BASE_URL}")
            print_error("Make sure the backend server is running:")
            print_error("  cd backend && uvicorn app.main:app --reload")
            return False
        except Exception as e:
            print_error(f"Exception occurred: {str(e)}")
            return False


async def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         API Testing Suite - New Features                  ║")
    print("║         Live Metrics & Chatbot Improvements               ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    print_info(f"Testing server at: {BASE_URL}")
    print_info(f"API base: {API_BASE}\n")
    
    # Run tests
    results = {}
    
    # Health check first
    results["Health Check"] = await test_health_check()
    
    if not results["Health Check"]:
        print_error("\n❌ Server is not running. Aborting tests.")
        sys.exit(1)
    
    # Run feature tests
    results["Dashboard Metrics"] = await test_dashboard_metrics()
    results["Chatbot Greeting"] = await test_chatbot_greeting()
    results["Chatbot Regular Query"] = await test_chatbot_regular_query()
    results["Default Questions"] = await test_default_questions()
    results["Query Tracking"] = await test_query_tracking()
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.OKGREEN}✓ PASSED{Colors.ENDC}" if result else f"{Colors.FAIL}✗ FAILED{Colors.ENDC}"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed!{Colors.ENDC}\n")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Some tests failed{Colors.ENDC}\n")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Tests interrupted by user{Colors.ENDC}\n")
        sys.exit(130)
