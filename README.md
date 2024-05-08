## Video Demonstration

<video width="320" height="240" controls>
  <source src="demo-video.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

## Setup and Configuration

### Imports and Global Variables
- **FastAPI** and other modules are imported for creating the API, handling CORS, and interacting with the OpenAI API.
- Loads environment variables and initializes the OpenAI client using the API key.

### FastAPI and Middleware Configuration
- Initializes a **FastAPI** application.
- Configures **CORS middleware** to allow requests from all origins, which should be restricted in production for security.

## File and Directory Management

### Directory and File Setup
- Ensures necessary directories and files are created before the application runs to prevent runtime errors related to file paths.

## API Endpoints

### Generating and Managing Code
- `@app.post("/generatecode/")`: Generates Python code snippets based on user input using the OpenAI API, saves the conversation history, and returns the code as HTML.
- `@app.post("/feedbackgeneratecode/")`: Generates code based on user feedback on previously generated snippets.

### Test Case Generation
- `@app.post("/generatetestcases/")`: Generates test cases for previously generated code snippets.
- `@app.post("/feedbacktestcases/")`: Modifies generated test cases based on user feedback.

### Execution of Code
- `@app.post("/runtestcases/")`: Executes code and test cases, captures outputs and errors, and returns the results.
- `@app.post("/regenraterun/")`: Regenerates and runs code based on feedback to correct errors from previous executions.

## Utility Functions

### Saving and Logging
- Includes functions to save conversations and code to JSON files for data persistence.

## Notes
- Utilizes environment variables to securely manage sensitive information.
- CORS settings are permissive, suitable for development but should be restricted in production.
- Manages state and persistence through saved conversations and code snippets, allowing for historical referencing and modifications.


## HTML Structure and Features

### Head
- **Meta Tags**: Sets character encoding to UTF-8 and viewport settings for responsive design.
- **Styles**: Includes inline CSS for styling session tabs and colors for current and other sessions.
- **External Stylesheets**:
  - Tailwind CSS for utility-first styles.
  - Highlight.js for syntax highlighting of code snippets.

### Title
- Sets the webpage title to "Code Snippet Generator".

### Body Layout
- **Flex Container**: Divides the page into a left column for snippet management and a right column for the editor and controls.

#### Left Column
- Displays a list of snippets and a button to create new snippets.
- Each snippet can be interactively selected, which changes its appearance and potentially its functionality.

#### Right Column
- Contains a text area for describing a new code snippet.
- Buttons to generate code, improve code, and generate test cases.
- Dynamic areas (`responseArea`, `responseArea1`, `responseArea2`) to display generated code, test cases, and test results respectively.
- Inputs and buttons for providing feedback on code and test cases and for running test code.

### Interactive Features
- **Session Management**:
  - Uses sessionStorage to manage and persist user sessions.
  - Functions to add and manage session tabs, including creating new sessions and deleting existing ones.
  
- **Code Generation**:
  - Event listeners tied to buttons for generating code, handling code feedback, generating and handling feedback on test cases, and running test cases.
  - Fetch API is used to communicate with a backend presumably set up with FastAPI (or similar), sending session details and user input, and receiving generated code or responses.

- **Highlight.js**:
  - Used for syntax highlighting the displayed code snippets and test cases.

### Scripting
- Extensive JavaScript is embedded directly within the HTML to handle UI interactions and API communications.
- JavaScript functions for session management, UI updates, fetching data from the server, and dynamically updating content based on server responses.

## Usage and Functionality
- The HTML file is designed to support an interactive web application where users can generate, improve, and test code snippets.
- It likely interacts with a server-side API that handles code generation requests and returns executable code or errors based on user input.
- Session data is dynamically managed in the client's browser to ensure persistence and state management during the user's interaction with the application.
