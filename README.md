# TextToGraph

TextToGraph is a Flask-based web application that transforms unstructured text into structured knowledge graphs using Natural Language Processing (NLP). The app allows users to upload a text file, extracts entities and relations using spaCy, and visualizes the resulting knowledge graph as an interactive network using NetworkX and Matplotlib. The interface is styled with Tailwind CSS for a modern, responsive design, making it user-friendly for both desktop and mobile users.

## Features
- **Text Upload**: Upload a text file via a sleek web interface.
- **Entity Extraction**: Uses spaCy’s Named Entity Recognition (NER) to identify entities such as PERSON, ORG, and GPE.
- **Relation Extraction**: Identifies simple relations (e.g., subject-verb-object) using dependency parsing.
- **Knowledge Graph Visualization**: Generates and displays a knowledge graph as a PNG image, with nodes (entities) and edges (relations).
- **Responsive Design**: Modern, Tailwind CSS-styled interface for an appealing user experience.
- **Error Handling**: Validates file uploads and provides clear error messages.

## Project Structure
```
TextToGraph/
├── app.py                    # Main Flask application
├── templates/
│   └── index.html            # HTML template for the web interface
├── static/                   # Folder for static files (e.g., output images)
├── uploads/                  # Folder for uploaded text files
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

**Note**: The spaCy model (`en_core_web_sm`) is downloaded automatically during setup.

## Prerequisites
- **Python**: Version 3.8 or higher.
- **System Requirements**: At least 4GB RAM and a modern CPU for running spaCy and NetworkX. GPU is not required.

## Setup Instructions
Follow these steps to set up and run the Flask app locally.

### 1. Clone the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/sohaibzafar701/TextToGraph.git
cd TextToGraph
```

### 2. Create a Virtual Environment
Create and activate a Python virtual environment to manage dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
Install the required Python packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```
The `requirements.txt` includes:
- `Flask==2.3.3`
- `spacy==3.7.2`
- `networkx==3.3`
- `matplotlib==3.9.2`
- `numpy==1.26.4`

**Note**: Installation may take time due to spaCy and its model. Ensure a stable internet connection. If issues arise, install packages individually:
```bash
pip install flask spacy networkx matplotlib numpy
```

### 4. Download spaCy Model
Download the spaCy English model used for NLP processing:
```bash
python -m spacy download en_core_web_sm
```

### 5. Create Required Folders
Ensure the `uploads` and `static` folders exist for storing temporary files:
```bash
mkdir -p uploads static
```

### 6. Run the Flask App
Start the Flask development server:
```bash
python app.py
```
The app will run on `http://localhost:5000`. Open this URL in a web browser.

## Usage
1. **Access the Web Interface**:
   - Navigate to `http://localhost:5000` in your browser.
   - You’ll see a modern interface with a gradient background and a file upload form styled using Tailwind CSS.

2. **Upload a Text File**:
   - Click the file input to select a text file (`.txt`) containing unstructured text.
   - Click **Upload and Analyze** to process the file.

3. **View Results**:
   - The app displays:
     - A knowledge graph as a PNG image, with nodes representing entities (e.g., PERSON, ORG) and edges representing relations (e.g., subject-verb-object).
     - A list of extracted entities and relations above the graph.
     - If no entities/relations are detected, a message indicates "No entities or relations found."
   - The graph is saved temporarily in the `static` folder and displayed on the page.

4. **Sample Input**:
   Create a `sample.txt` file with content like:
   ```
   Elon Musk founded Tesla in 2003. Tesla is based in California.
   ```
   Upload it to see entities (e.g., "Elon Musk", "Tesla", "California") and relations (e.g., "Elon Musk - founded - Tesla") visualized.

5. **Troubleshooting**:
   - Ensure the text file is valid and contains meaningful content for entity/relation extraction.
   - Check the console for errors if spaCy fails to process or the graph fails to render.

## Expected Outputs
- **Entities**: spaCy extracts entities like `PERSON` (e.g., "Elon Musk"), `ORG` (e.g., "Tesla"), `GPE` (e.g., "California").
- **Relations**: Simple triples (e.g., "Elon Musk - founded - Tesla") based on dependency parsing.
- **Knowledge Graph**: A visual network where nodes are entities and edges are relations, saved as a PNG.

## Troubleshooting
- **spaCy Model Errors**:
  - Ensure the `en_core_web_sm` model is installed (`python -m spacy download en_core_web_sm`).
  - Verify compatibility with your Python version (3.8–3.10 recommended).
- **Dependency Installation Issues**:
  - If installation is slow, try installing packages individually:
    ```bash
    pip install flask
    pip install spacy
    pip install networkx matplotlib numpy
    ```
  - Upgrade pip: `pip install --upgrade pip setuptools wheel`.
  - Clear pip cache if disk space is an issue: `pip cache purge`.
- **File Upload Errors**:
  - Ensure the uploaded file is a valid `.txt` file with readable text.
  - Check that the `uploads` and `static` folders are writable.
- **Server Not Starting**:
  - Ensure port `5000` is free. If not, change the port in `app.py`:
    ```python
    app.run(host='0.0.0.0', port=8000)
    ```
- **No Entities/Relations Detected**:
  - Verify the input text contains recognizable entities (e.g., names, organizations).
  - Check spaCy’s NER model performance on your text; consider using a larger model (e.g., `en_core_web_md`) for better accuracy.
- **Graph Not Displaying**:
  - Ensure Matplotlib is installed and the `static` folder is writable.
  - Check console logs for NetworkX or Matplotlib errors.

## Performance Tips
- **Text Size**: Large text files may slow down processing. Consider limiting input to a few paragraphs for faster response.
- **spaCy Model**: The default `en_core_web_sm` model is lightweight but may miss complex relations. Upgrade to `en_core_web_md` or `en_core_web_lg` for better accuracy at the cost of more memory.
- **Memory Usage**: Monitor system resources, as spaCy and NetworkX can be memory-intensive for large graphs.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- **spaCy**: For NLP and entity/relation extraction.
- **NetworkX**: For knowledge graph construction.
- **Matplotlib**: For graph visualization.
- **Flask**: For the web framework.
- **Tailwind CSS**: For the responsive, modern interface.

---
*Built with ❤️ by Sohaib Zafar*  
*Last updated: June 2025*
