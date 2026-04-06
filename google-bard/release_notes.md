#### Following enhancements have been made to the Google Gemini Connector in version 2.1.0:

- We’ve removed the `Generate Message` action and moved its functionality into `Generate Text` action.
- Upgraded the connector to use the latest APIs, as the older Gemini APIs have been deprecated.
- Introduced new parameters in the `Generate Text` action:
    - Contents
    - System Instructions
    - Thinking levels
- Removed the following parameters from the `Generate Text` action:
    - Text Prompt
    - Candidate Count
- Renamed the parameter `Text` to `Content` in the `Generate Embedding` action.
- Introduced new parameters in the `Generate Embedding` action:
    - Task Type
    - Output Dimensionality
- Removed the following parameters from the `Count Message Token` action:
    - Context
    - Examples
- Updated the output schema across all actions.