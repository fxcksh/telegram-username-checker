# 💥Telegram Username Validator and Checker💥
This Python script checks if a Telegram username is available or taken using the [fragment](https://fragment.com/) website and the [telegram](https://t.me/) web resource. No API key is required!

#### 🪲 MIND BUG WHEN USING:
The script may currently produce false positives when identifying free usernames. This is due to Telegram’s reserved usernames, which are set aside for internal purposes. Additionally, there can be a delay before a username that has recently become available can be reused, so that username also may be marked as free but setting it is not available right now. I will fix it soon!

### Installation and Running (Locally)
1. Clone the repository and navigate into the directory:
```
git clone https://github.com/S4kur4H4run0/telegram-username-grabber.git
cd telegram-username-grabber
```
3. Create a virtual environment:
```
python3.12 -m venv env
```

5. Activate the virtual environment:
```
source env/bin/activate
```

7. Install the required packages:
```
pip install -r requirements.txt
```

### Running the Script
To run the script locally, use the following command:

`python script.py --file https://raw.githubusercontent.com/path/to/usernames/list.txt --verbose`

Replace script.py with the actual name of your Python script.

- The --file argument specifies the URL or path to the list of usernames.
- The --verbose flag enables detailed logging output.

### Running in GitHub Actions
To test the script in the GitHub Actions environment, create an issue using the Payload request template. In the issue body, provide a single URL and wait for approval to run the pipeline. 🥏

### Payload Limitations

- Only files hosted on raw.githubusercontent.com are supported.
- Usernames must be listed one per line.
- For format reference, see this [example](https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/Names/names.txt) file.

### The results of workflow runs are accessible on the Actions page

[<img width="971" alt="Screenshot 2024-08-08 105111" src="https://github.com/user-attachments/assets/6f732206-ad69-40b6-b2d1-b8729f19a848">](https://github.com/fxcksh/telegram-username-grabber/actions/runs/10307476989)

#### Remember, a cool username is not worth account or username theft. Choose any username you want by brute-forcing with your list ❤️‍🩹

             
⎛⎝ ≽ > [⩊](https://t.me/+ICPFhQ-JTGhmZjc6) < ≼ ⎠⎞
        

