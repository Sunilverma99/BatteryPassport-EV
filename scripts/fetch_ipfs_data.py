import requests
import base64

def fetch_ipfs_data():
    # Filebase API endpoint
    url = f"https://api.filebase.io/v1/ipfs/QmYdCcEPr8R8Cp8XdEB5CP1EANg91B7cSTQk3Su6ZNnZEq"
    
    # Encode the Root Key and Secret
    credentials = "D2E36D112C666892F8D3:ktaqZO2S5RXGAZIKLkjYFxEoEScfOyy2mTyvufs5"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    # Set up the request headers
    headers = {
        "Authorization": f"Bearer {encoded_credentials}"
    }
    
    try:
        # Make the GET request
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Return the content
            return response.content
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            return None
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def main():
    data = fetch_ipfs_data()
    if data:
        print("Successfully retrieved data from IPFS:")
        print(data)
    else:
        print("Failed to retrieve data from IPFS")

if __name__ == "__main__":
    main()