<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>README for KlingAI Virtual Try-On</title>
</head>
<body>
    <h1>KlingAI Virtual Try-On</h1>
    <p>This project utilizes the KlingAI API to provide a virtual try-on experience using images of people and garments.</p>

    <h2>Features</h2>
    <ul>
        <li>Upload images of a person and a garment.</li>
        <li>Generate a virtual try-on image by combining the two inputs.</li>
        <li>Random seed option for varied results.</li>
        <li>Responsive Gradio interface for user-friendly interaction.</li>
    </ul>

    <h2>Installation</h2>
    <p>To set up the project, clone the repository and install the required packages:</p>
    <pre><code>git clone 
cd <repository_directory>
pip install -r requirements.txt</code></pre>

    <h2>Usage</h2>
    <p>Run the application using the following command:</p>
    <pre><code>python app.py</code></pre>
    <p>Open the provided link in your browser to access the Gradio interface.</p>

    <h2>Input Images</h2>
    <p>Make sure to provide valid images of people and garments in the specified formats. The application expects:</p>
    <ul>
        <li>Person images: <code>assets/human/</code></li>
        <li>Garment images: <code>assets/cloth/</code></li>
    </ul>

    <h2>License</h2>
    <p>This project is licensed under the MIT License. See the <a href="LICENSE">LICENSE</a> file for more details.</p>

    <h2>Contact</h2>
    <p>For questions or suggestions, feel free to reach out:</p>
</body>
</html>
