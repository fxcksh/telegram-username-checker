---
name: Payload Request
about: Request to test the script in the GitHub Actions environment
title: "[Payload Request]"
labels: payload, request
assignees: fxcksh

---

### Request Details

**URL to the Username List:**
Provide the URL of the file hosted on `raw.githubusercontent.com` containing the list of usernames. The file should have usernames listed one per line.

Example: `https://raw.githubusercontent.com/username/repository/branch/filename.txt`

### Example File Format

Usernames must be listed one per line. For reference, you can check this [example file](https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/Names/names.txt).

### Acceptance Criteria

- The URL should be valid and accessible.
- Usernames should be formatted correctly with each username on a new line.
- Ensure there are no additional instructions or files not related to the username list.

Thank you for your request! Please wait for approval to run the pipeline. 🥏
