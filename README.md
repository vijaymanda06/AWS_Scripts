# AWS EC2 Instance Scanner with Slack Integration

This is a Python script that scans all your AWS regions and finds every single EC2 instance you have running or stopped. It's like having a complete inventory of your AWS infrastructure that gets automatically sent to your Slack channel.

## What This Script Actually Does

When you run this script, it:

1. **Connects to your AWS account** and shows you which profile you're using, your account ID, and default region
2. **Scans every single AWS region** - all 22 of them - to find your EC2 instances
3. **Collects detailed information** about each instance including:
   - Basic stuff: ID, name, type, whether it's running or stopped
   - Network details: private IP, public IP, VPC, subnet, availability zone
   - Security info: security groups
   - When it was launched and what platform it runs on
4. **Creates a professional Excel report** with color coding (green for running instances, red for stopped ones)
5. **Automatically uploads the report to Slack** so your team can see it immediately

## What You Get

### Excel Report
The script creates an Excel file with:
- A main sheet showing all your instances with nice formatting
- Color-coded rows (green = running, red = stopped)
- Filters on every column so you can sort and search
- A summary sheet with counts by region, instance type, and state

### Slack Integration
- The bot automatically posts the Excel file to your Slack channel
- Shows a summary of how many instances were found
- Includes a preview of the report right in Slack
- Works with both public and private channels

## Screenshots

### Excel Report Output
![Excel Report](SS1.jpg)
*This shows what the generated Excel file looks like - clean, professional, and easy to read*

### Slack Notification
![Slack Integration](SS2.jpg)
*The bot automatically posts reports to your Slack channel with file previews*

### Terminal Output
![Script Execution](SS3.jpg)
![Script Execution](SS4.jpg)
*What you see when running the script - real-time progress and status updates*

## Prerequisites

Before you can use this script, you need:

### 1. Python 3
Make sure you have Python 3 installed on your computer. You can download it from python.org if you don't have it.

### 2. AWS Access
You need access to an AWS account and the ability to list EC2 instances. The easiest way to set this up is:

```bash
aws configure
```

This will ask for:
- Your AWS Access Key ID
- Your AWS Secret Access Key  
- Default region (like us-east-1)
- Output format (just press Enter for json)

### 3. Slack Bot Setup
You need to create a Slack app and get a bot token. Here's how:

#### Step 1: Create a Slack App
1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Give it a name like "AWS Report Bot" and select your workspace

#### Step 2: Add Bot Permissions
1. In your app, go to "OAuth & Permissions" in the left sidebar
2. Under "Scopes", add these Bot Token Scopes:
   - `files:write` - to upload files
   - `chat:write` - to send messages
   - `channels:read` - to read channel info
3. Click "Install to Workspace" at the top

#### Step 3: Get Your Bot Token
1. After installing, copy the "Bot User OAuth Token" (starts with `xoxb-`)
2. This is your `SLACK_BOT_TOKEN`

#### Step 4: Get Channel ID
1. In Slack, right-click on the channel you want to use
2. Select "View channel details"
3. Scroll down to find the Channel ID (starts with C for public, G for private)
4. This is your `SLACK_CHANNEL_ID`

#### Step 5: Invite Bot to Channel
1. In your Slack channel, type: `/invite @YourBotName`
2. Replace "YourBotName" with whatever you named your bot

## Installation

### 1. Download the Script
Get the `complete_ec2_scanner_with_slack.py` file and put it in a folder on your computer.

### 2. Install Python Dependencies
Open your terminal/command prompt in the folder with the script and run:

```bash
pip install -r requirements.txt
```

This installs:
- `boto3` - for talking to AWS
- `pandas` - for handling data and creating Excel files
- `openpyxl` - for Excel file support
- `xlsxwriter` - for nice Excel formatting

### 3. Set Environment Variables
You need to tell the script your Slack bot token and channel ID. You can do this in a few ways:

#### Option A: Set them in your system (recommended)
**Windows:**
```bash
setx SLACK_BOT_TOKEN "xoxb-your-token-here"
setx SLACK_CHANNEL_ID "C1234567890"
```

**Mac/Linux:**
```bash
export SLACK_BOT_TOKEN="xoxb-your-token-here"
export SLACK_CHANNEL_ID="C1234567890"
```

#### Option B: Set them just for this session
**Windows:**
```bash
set SLACK_BOT_TOKEN=xoxb-your-token-here
set SLACK_CHANNEL_ID=C1234567890
```

**Mac/Linux:**
```bash
export SLACK_BOT_TOKEN="xoxb-your-token-here"
export SLACK_CHANNEL_ID="C1234567890"
```

## How to Use

### 1. Run the Script
In your terminal, navigate to the folder with the script and run:

```bash
python complete_ec2_scanner_with_slack.py
```

### 2. What Happens
The script will:
1. Check your Slack configuration and test the connection
2. Show your current AWS profile and account info
3. Start scanning all AWS regions for EC2 instances
4. Display what it finds in real-time
5. Create an Excel report with a timestamp in the filename
6. Upload the report to your Slack channel automatically

### 3. Check the Results
- Look for the Excel file in the same folder (named like `AWS_EC2_Instances_20250810_213648.xlsx`)
- Check your Slack channel for the uploaded report
- The terminal will show you exactly what happened

## What the Output Looks Like

### Terminal Output
You'll see real-time updates like:
```
🔍 DEBUG: Environment Variables
SLACK_BOT_TOKEN: xoxb-78567...EKfq
SLACK_CHANNEL_ID: C099KAFESH1

🏷️  Current Profile: default
📋 Account ID: 823151423293
👤 User: vijaymanda
🌍 Default Region: ap-south-1

✅ Token verified - Bot Name: awsreportbot
✅ Successfully connected to #aws_reports

🚀 Starting AWS EC2 Instance Discovery...

--- Starting EC2 Instance Check Across All Regions ---

Searching in region: ap-south-1...
Instance ID            Instance Name             Instance Type   State        Private IP      Public IP      
---------------------  ------------------------  --------------  -----------  --------------  -------------- 
i-03208ae03e599bb3a    Monitoring                t3.micro        stopped      172.31.14.130   N/A
i-02691ea557ed1a0d5    Ubuntu_Apps               t3.micro        stopped      172.31.7.160    N/A
Found 2 instances in ap-south-1

✅ Excel report created successfully: AWS_EC2_Instances_20250810_212745.xlsx
📤 Uploading report to Slack...
✅ Report successfully uploaded to Slack!
```

### Excel Report
The Excel file will have:
- A blue header with "AWS EC2 Instances Report"
- Summary info showing total instances and when it was generated
- A table with all your instance details
- Color-coded rows (green for running, red for stopped)
- Filters on every column for easy searching

### Slack Message
In your Slack channel, you'll see:
- A message from your bot with the report summary
- The Excel file attached and ready to download
- A preview of the report content

## Troubleshooting

### Common Issues

**"SLACK_BOT_TOKEN not found"**
- Make sure you set the environment variable correctly
- Check that it starts with `xoxb-`
- Try setting it again and restarting your terminal

**"Channel not found or bot doesn't have access"**
- Make sure you invited the bot to the channel with `/invite @YourBotName`
- Check that the channel ID is correct
- Verify the bot has the right permissions

**"Token verification failed"**
- Your bot token might be expired or invalid
- Go back to your Slack app settings and regenerate the token
- Make sure you copied the Bot User OAuth Token, not the User OAuth Token

**"Access denied to region"**
- Some regions might not be enabled for your account
- This is normal and won't affect the script - it will just skip those regions

**Excel file creation fails**
- The script will automatically create a CSV file instead
- Make sure you have the required Python packages installed

### Getting Help

If something isn't working:
1. Check the terminal output for error messages
2. Make sure your AWS credentials are set up correctly
3. Verify your Slack bot has the right permissions
4. Check that the bot is invited to your channel

## What This Tool is Good For

This script is perfect when you need to:
- **Get a complete overview** of all your EC2 instances across all regions
- **Share infrastructure status** with your team via Slack
- **Create reports** for security audits or compliance
- **Track costs** by seeing what instances you have and their states
- **Document your infrastructure** for planning or troubleshooting

## File Structure

Your folder should look like this:
```
AWS_Scripts/
├── complete_ec2_scanner_with_slack.py  # The main script
├── requirements.txt                     # Python dependencies
├── README.md                           # This file
└── AWS_EC2_Instances_*.xlsx           # Generated reports (after running)
```

## Support

If you run into issues:
1. Check the terminal output for specific error messages
2. Verify your AWS and Slack setup
3. Make sure all environment variables are set correctly

The script includes detailed error messages and will tell you exactly what's wrong and how to fix it.
