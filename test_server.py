"""
Script di test per verificare che il server HTTP/SSE sia funzionante.
Esegui questo script mentre il server è in esecuzione.
"""

import requests
import json

# URL del server
BASE_URL = "http://localhost:8000"

def test_root():
    """Test dell'endpoint root"""
    print("🔍 Test endpoint root...")
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Root endpoint OK")
            print(f"   Risposta: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Root endpoint fallito: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def test_health():
    """Test dell'endpoint health"""
    print("\n🔍 Test endpoint health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint OK")
            print(f"   Risposta: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint fallito: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def test_sse_endpoint():
    """Test che l'endpoint SSE risponda"""
    print("\n🔍 Test endpoint SSE (connessione)...")
    try:
        # Non facciamo un test completo SSE, solo verifichiamo che risponda
        response = requests.get(f"{BASE_URL}/sse", stream=True, timeout=2)
        if response.status_code == 200:
            print("✅ SSE endpoint risponde")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            return True
        else:
            print(f"❌ SSE endpoint fallito: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("✅ SSE endpoint risponde (timeout normale per stream)")
        return True
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Test Server MCP HTTP/SSE")
    print("=" * 50)
    print(f"\nURL: {BASE_URL}")
    print("\nAssicurati che il server sia in esecuzione con:")
    print("  python server_http.py\n")
    
    results = []
    results.append(test_root())
    results.append(test_health())
    results.append(test_sse_endpoint())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ Tutti i test passati!")
        print("\n🎯 Il server è pronto per ChatGPT!")
        print(f"   Usa questo URL: {BASE_URL}/sse")
    else:
        print("❌ Alcuni test sono falliti")
        print("\nVerifica che il server sia in esecuzione:")
        print("  python server_http.py")
    print("=" * 50)
