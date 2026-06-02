#### The following enhancements have been made to the Google Gemini connector in version 2.1.0:

- Removed the `Generate Message` action and merged its functionality into the `Generate Text` action. 
- Upgraded the connector to use the latest Gemini APIs, as the legacy APIs have been deprecated.
- Added the following parameters to the `Generate Text` action:
    - Contents
    - System Instructions
    - Thinking levels
- Removed the following parameters from the `Generate Text` action: 
    - Text Prompt
    - Candidate Count
- Renamed the `Text` parameter to `Content` in the `Generate Embedding` action. 
- Added the following parameters to the `Generate Embedding` action:
    - Task Type
    - Output Dimensionality
- Removed the following parameters from the `Count Message Token` action: 
    - Context
    - Examples
- Updated the output schemas across all actions.