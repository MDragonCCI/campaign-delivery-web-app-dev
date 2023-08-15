from website import create_app
import secure

app = create_app()

if __name__ == "__main__":
    app.run(debug = True)

secure_headers = secure.Secure()
 
@app.after_request
def set_secure_headers(response):
    secure_headers.framework.flask(response)
    return response


