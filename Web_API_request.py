import requests

url = "http://localhost:5000/process"
data = {
    "reference": "data/A_ref.JPG",
    "experiment": "data/A_exp.JPG"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    print("Data:", result["data"])
    import pdb 
    pdb.set_trace()
    print("Images:", result["images"].keys())  
else:
    print("Error:", response.status_code, response.text)
