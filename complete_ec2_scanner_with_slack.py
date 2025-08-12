import boto3
from botocore.exceptions import ClientError
import pandas as pd
from datetime import datetime
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time

def debug_env_variables():
    """Debug function to check environment variables"""
    # Try different methods to get environment variables
    bot_token = os.environ.get('SLACK_BOT_TOKEN', 'Not Set')
    channel_id = os.environ.get('SLACK_CHANNEL_ID', 'Not Set')
    
    print("\n🔍 DEBUG: Environment Variables")
    if bot_token and bot_token != 'Not Set':
        print(f"SLACK_BOT_TOKEN: {'*' * (len(bot_token) - 8)}{bot_token[-4:]}")
    else:
        print("SLACK_BOT_TOKEN: Not Set")
        
    print(f"SLACK_CHANNEL_ID: {channel_id}")
    
    # Try to read from process environment
    import subprocess
    try:
        # REPLACE lines 32-35 with this secure Windows registry approach:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                try:
                    user_token = winreg.QueryValueEx(key, "SLACK_BOT_TOKEN")[0]
                except FileNotFoundError:
                    user_token = None
                try:
                    user_channel = winreg.QueryValueEx(key, "SLACK_CHANNEL_ID")[0]
                except FileNotFoundError:
                    user_channel = None
        except ImportError:
            # Fallback for non-Windows systems
            user_token = None
            user_channel = None
        
        print("\nUser Environment Variables:")
        if user_token and user_token != 'Not Set':
            print(f"User SLACK_BOT_TOKEN: {'*' * (len(user_token) - 8)}{user_token[-4:]}")
        else:
            print("User SLACK_BOT_TOKEN: Not Set")
        if user_channel:
            print(f"User SLACK_CHANNEL_ID: {user_channel}")
        else:
            print("User SLACK_CHANNEL_ID: Not Set")
            
        # If we found values in User environment but not in process, set them
        if bot_token == 'Not Set' and user_token:
            os.environ['SLACK_BOT_TOKEN'] = user_token
            print("✅ Loaded SLACK_BOT_TOKEN from User environment")
        if channel_id == 'Not Set' and user_channel:
            os.environ['SLACK_CHANNEL_ID'] = user_channel
            print("✅ Loaded SLACK_CHANNEL_ID from User environment")
            
    except Exception as e:
        print(f"Error checking User environment: {str(e)}")
    
    # Check if variables are in process environment
    all_env = os.environ.keys()
    print("\nFound Environment Variables:")
    slack_vars_found = False
    for key in all_env:
        if 'SLACK' in key:
            slack_vars_found = True
            print(f"Found: {key}")
    
    if not slack_vars_found:
        print("No Slack-related environment variables found")

def verify_slack_token():
    """Verify Slack token is valid"""
    bot_token = os.environ.get('SLACK_BOT_TOKEN')
    
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN not found in environment")
        return False
        
    try:
        response = requests.post(
            "https://slack.com/api/auth.test",
            headers={"Authorization": f"Bearer {bot_token}"},
            verify=True,  # Enforce SSL verification
            timeout=30    # Add timeout protection
        ).json()
        
        if response.get("ok"):
            print(f"✅ Token verified - Bot Name: {response.get('user')}")
            print(f"   Team: {response.get('team')}")
            return True
        else:
            print(f"❌ Token verification failed: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        return False

def show_current_profile_info():
    """Display current AWS profile and account information"""
    try:
        # Get current profile
        current_profile = os.environ.get('AWS_PROFILE', 'default')
        
        # Get account info
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        # Get region
        session = boto3.Session()
        region = session.region_name
        
        print(f"🏷️  Current Profile: {current_profile}")
        print(f"📋 Account ID: {identity['Account']}")
        print(f"👤 User: {identity['Arn'].split('/')[-1]}")
        print(f"🌍 Default Region: {region}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error getting profile info: {e}")
        print("=" * 60)

def check_slack_channel_access(bot_token, channel_id):
    """Verify bot access to the specified channel"""
    try:
        response = requests.post(
            "https://slack.com/api/conversations.info",
            headers={"Authorization": f"Bearer {bot_token}"},
            data={"channel": channel_id},
            verify=True,  # Enforce SSL verification
            timeout=30    # Add timeout protection
        ).json()
        
        if not response.get("ok"):
            error = response.get("error", "unknown error")
            if error == "channel_not_found":
                print("❌ Channel not found or bot doesn't have access")
                print("🔧 For channels, ensure:")
                print("   1. Bot is invited using: /invite @YourBotName")
                print("   2. Channel ID is correct")
                return False
            print(f"❌ Channel access error: {error}")
            return False
            
        channel_info = response.get("channel", {})
        channel_type = "private" if channel_info.get("is_private") else "public"
        print(f"✅ Successfully connected to {channel_type} channel: {channel_info.get('name')}")
        return True
        
    except Exception as e:
        print(f"❌ Error checking channel access: {e}")
        return False

def check_slack_configuration():
    """Checks and displays the status of Slack environment variables at startup."""
    print("🔎 Checking Slack Configuration...")
    bot_token = os.environ.get('SLACK_BOT_TOKEN')
    channel_id = os.environ.get('SLACK_CHANNEL_ID')
    is_config_ok = True

    if bot_token and bot_token.startswith("xoxb-"):
        print("✅ SLACK_BOT_TOKEN: Valid format")
    else:
        print("❌ SLACK_BOT_TOKEN: Not set or invalid format")
        print("   Must start with 'xoxb-'")
        is_config_ok = False

    if channel_id and (channel_id.startswith("C") or channel_id.startswith("G")):
        print("✅ SLACK_CHANNEL_ID: Valid format")
        if not check_slack_channel_access(bot_token, channel_id):
            is_config_ok = False
    else:
        print("❌ SLACK_CHANNEL_ID: Not set or invalid format")
        print("   Must start with 'C' (public) or 'G' (private)")
        is_config_ok = False

    if not is_config_ok:
        print("\n⚠️ Slack integration will be disabled")
    else:
        print("\n✅ Slack integration is ready")
    
    print("=" * 60)
    return is_config_ok

def list_instances_across_all_regions():
    """
    Connects to AWS and lists all EC2 instances across all available regions,
    including their ID, Name tag, type, current state, and IP addresses.
    Exports results to an Excel file with formatting.
    """
    # A client is needed to get the list of all regions
    ec2_client = boto3.client('ec2')
    
    try:
        # Retrieves all regions that are available for the account
        all_regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    except ClientError as e:
        print(f"Could not retrieve AWS regions. Error: {e}")
        return
    
    print("--- Starting EC2 Instance Check Across All Regions ---")
    
    # List to store all instance data for Excel export
    all_instances_data = []
    
    for region in all_regions:
        print(f"\nSearching in region: {region}...")
        
        try:
            # Create an EC2 resource for the specific region
            ec2_resource = boto3.resource('ec2', region_name=region)
            
            instances = list(ec2_resource.instances.all())
            if not instances:
                print("No instances found.")
                continue
                
            # Print a header for the instance details
            print(f"{'Instance ID':<22} {'Instance Name':<25} {'Instance Type':<15} {'State':<12} {'Private IP':<15} {'Public IP':<15}")
            print(f"{'-'*21:<22} {'-'*24:<25} {'-'*14:<15} {'-'*11:<12} {'-'*14:<15} {'-'*14:<15}")
            
            region_instance_count = 0
            for instance in instances:
                # The 'Name' tag is retrieved separately
                instance_name = "N/A"
                if instance.tags:
                    for tag in instance.tags:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                            break
                
                # Get IP addresses
                private_ip = instance.private_ip_address if instance.private_ip_address else "N/A"
                public_ip = instance.public_ip_address if instance.public_ip_address else "N/A"
                
                # Get additional details for Excel
                vpc_id = instance.vpc_id if instance.vpc_id else "N/A"
                subnet_id = instance.subnet_id if instance.subnet_id else "N/A"
                availability_zone = instance.placement['AvailabilityZone'] if instance.placement else "N/A"
                launch_time = instance.launch_time.strftime('%Y-%m-%d %H:%M:%S UTC') if instance.launch_time else "N/A"
                
                # Get security groups
                security_groups = ", ".join([sg['GroupName'] for sg in instance.security_groups]) if instance.security_groups else "N/A"
                
                # Print to console
                print(f"{instance.id:<22} {instance_name:<25} {instance.instance_type:<15} {instance.state['Name']:<12} {private_ip:<15} {public_ip:<15}")
                
                # Store data for Excel export
                instance_data = {
                    'Region': region,
                    'Instance ID': instance.id,
                    'Instance Name': instance_name,
                    'Instance Type': instance.instance_type,
                    'State': instance.state['Name'],
                    'Private IP': private_ip,
                    'Public IP': public_ip,
                    'VPC ID': vpc_id,
                    'Subnet ID': subnet_id,
                    'Availability Zone': availability_zone,
                    'Security Groups': security_groups,
                    'Launch Time': launch_time,
                    'Platform': instance.platform if instance.platform else "Linux/UNIX"
                }
                all_instances_data.append(instance_data)
                region_instance_count += 1
            
            print(f"Found {region_instance_count} instances in {region}")
            
        except ClientError as e:
            # This handles regions that might not be enabled for your account
            if e.response['Error']['Code'] == 'UnauthorizedOperation':
                print(f"Access denied to region {region}. It may not be enabled for your account.")
            else:
                print(f"An unexpected error occurred in region {region}: {e}")
    
    # Create Excel file if instances were found
    if all_instances_data:
        filename = create_excel_report(all_instances_data)
        print(f"\n--- Instance check complete. Total instances found: {len(all_instances_data)} ---")
        
        # Send report to Slack if configuration is valid
        if filename and check_slack_configuration():
            send_report_to_slack(filename, len(all_instances_data))
    else:
        print("No instances found to export.")

def create_excel_report(instances_data):
    """
    Creates a formatted Excel report with instance data
    Returns the filename if successful, None otherwise
    """
    try:
        # Create DataFrame
        df = pd.DataFrame(instances_data)
        total_instances = len(df)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"AWS_EC2_Instances_{timestamp}.xlsx"
        
        # Create Excel writer with xlsxwriter engine for formatting
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            # Write the main data
            df.to_excel(writer, sheet_name='EC2 Instances', index=False, startrow=3)
            
            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['EC2 Instances']
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })
            
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'fg_color': '#2F5597',
                'font_color': 'white',
                'align': 'center'
            })
            
            summary_format = workbook.add_format({
                'bold': True,
                'font_size': 12,
                'fg_color': '#D9E2F3'
            })
            
            cell_format = workbook.add_format({
                'text_wrap': True,
                'valign': 'top',
                'border': 1
            })
            
            running_format = workbook.add_format({
                'text_wrap': True,
                'valign': 'top',
                'border': 1,
                'fg_color': '#C6EFCE'
            })
            
            stopped_format = workbook.add_format({
                'text_wrap': True,
                'valign': 'top',
                'border': 1,
                'fg_color': '#FFC7CE'
            })
            
            # Write title
            worksheet.merge_range('A1:M1', 'AWS EC2 Instances Report', title_format)
            
            # Write summary
            worksheet.write('A2', f'Total Instances: {total_instances}', summary_format)
            worksheet.write('C2', f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', summary_format)
            
            # Apply header formatting
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(3, col_num, value, header_format)
            
            # Apply conditional formatting for running instances (green) and stopped (red)
            for row_num in range(len(df)):
                row_range = f'A{4 + row_num}:M{4 + row_num}'
                state = df.iloc[row_num]['State']
                
                if state == 'running':
                    worksheet.conditional_format(row_range, {
                        'type': 'no_errors',
                        'format': running_format
                    })
                elif state == 'stopped':
                    worksheet.conditional_format(row_range, {
                        'type': 'no_errors',
                        'format': stopped_format
                    })
                else:
                    worksheet.conditional_format(row_range, {
                        'type': 'no_errors',
                        'format': cell_format
                    })
            
            # Set column widths
            column_widths = {
                'A': 15,  # Region
                'B': 20,  # Instance ID
                'C': 25,  # Instance Name
                'D': 15,  # Instance Type
                'E': 12,  # State
                'F': 15,  # Private IP
                'G': 15,  # Public IP
                'H': 15,  # VPC ID
                'I': 15,  # Subnet ID
                'J': 20,  # Availability Zone
                'K': 30,  # Security Groups
                'L': 20,  # Launch Time
                'M': 15   # Platform
            }
            
            for col, width in column_widths.items():
                worksheet.set_column(f'{col}:{col}', width)
            
            # Freeze the header row
            worksheet.freeze_panes(4, 0)
            
            # Add auto filter
            worksheet.autofilter(3, 0, 3 + len(df), len(df.columns) - 1)
        
        print(f"\n✅ Excel report created successfully: {filename}")
        print(f"📍 File location: {os.path.abspath(filename)}")
        
        # Create summary sheet using the existing DataFrame
        create_summary_sheet(df, filename)
        return filename
        
    except ImportError:
        print("\n❌ Required libraries not found. Please install them using:")
        print("pip install pandas openpyxl xlsxwriter")
        print("\n⚠️ Creating CSV file as fallback...")
        return create_csv_fallback(instances_data)
    except Exception as e:
        print(f"\n❌ Error creating Excel file: {e}")
        print("\n⚠️ Creating CSV file as fallback...")
        return create_csv_fallback(instances_data)

def create_csv_fallback(instances_data):
    """
    Creates a CSV file if Excel creation fails
    Returns the filename if successful, None otherwise
    """
    try:
        import csv
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"AWS_EC2_Instances_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if instances_data:
                fieldnames = instances_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(instances_data)
        
        print(f"✅ CSV report created successfully: {filename}")
        print(f"📍 File location: {os.path.abspath(filename)}")
        return filename
        
    except Exception as e:
        print(f"❌ Error creating CSV file: {e}")
        return None

def create_summary_sheet(df, filename):
    """
    Adds a summary sheet to the existing Excel file using the provided DataFrame
    """
    try:
        # Create summary by region
        region_summary = df.groupby('Region').agg({
            'Instance ID': 'count',
            'State': lambda x: (x == 'running').sum()
        }).rename(columns={
            'Instance ID': 'Total Instances',
            'State': 'Running Instances'
        })
        region_summary['Stopped Instances'] = region_summary['Total Instances'] - region_summary['Running Instances']
        
        # Create summary by instance type
        type_summary = df.groupby('Instance Type').size().reset_index(name='Count')
        
        # Create summary by state
        state_summary = df.groupby('State').size().reset_index(name='Count')
        
        # Append to existing Excel file with proper mode handling
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            # Write summaries
            region_summary.to_excel(writer, sheet_name='Summary', startrow=2, startcol=0)
            type_summary.to_excel(writer, sheet_name='Summary', startrow=2, startcol=5, index=False)
            state_summary.to_excel(writer, sheet_name='Summary', startrow=2, startcol=8, index=False)
            
            # Get worksheet
            worksheet = writer.sheets['Summary']
            
            # Add headers
            worksheet['A1'] = 'Summary by Region'
            worksheet['F1'] = 'Summary by Instance Type'
            worksheet['I1'] = 'Summary by State'
            
            # Format headers
            from openpyxl.styles import Font
            for cell in ['A1', 'F1', 'I1']:
                worksheet[cell].font = Font(bold=True)
        
        print(f"📊 Summary sheet added to: {filename}")
        
    except Exception as e:
        print(f"⚠️  Could not create summary sheet: {e}")

def send_report_to_slack(filename, total_instances):
    """
    Uploads the report file to a Slack channel using the new Files API.
    Uses the modern 3-step upload process: get URL, upload file, complete upload.
    """
    bot_token = os.environ.get('SLACK_BOT_TOKEN')
    channel_id = os.environ.get('SLACK_CHANNEL_ID')

    if not bot_token or not channel_id:
        print("\n⚠️ Slack integration is disabled - missing configuration")
        return

    try:
        if not os.path.exists(filename):
            print(f"\n❌ File not found: {filename}")
            return

        file_size = os.path.getsize(filename)
        if file_size > 50 * 1024 * 1024:  # 50MB limit for Slack
            print("\n❌ File too large for Slack (max 50MB)")
            return

        print("\n📤 Uploading report to Slack...")

        # Step 1: Get upload URL
        print("   Step 1/3: Getting upload URL...")
        upload_url_response = requests.post(
            'https://slack.com/api/files.getUploadURLExternal',
            headers={
                'Authorization': f'Bearer {bot_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'filename': os.path.basename(filename),
                'length': file_size
            },
            verify=True,  # Enforce SSL verification
            timeout=30    # Add timeout protection
        )

        upload_url_data = upload_url_response.json()
        if not upload_url_data.get("ok"):
            print(f"❌ Failed to get upload URL: {upload_url_data.get('error')}")
            # Try fallback method
            print("🔄 Trying summary-only approach...")
            send_report_summary_only(total_instances)
            return

        upload_url = upload_url_data['upload_url']
        file_id = upload_url_data['file_id']

        # Step 2: Upload file to the URL
        print("   Step 2/3: Uploading file...")
        with open(filename, 'rb') as file_content:
            upload_response = requests.post(upload_url, files={'file': file_content}, verify=True, timeout=30)
            
        if upload_response.status_code != 200:
            print(f"❌ File upload failed with status: {upload_response.status_code}")
            print("🔄 Trying summary-only approach...")
            send_report_summary_only(total_instances)
            return

        # Step 3: Complete the upload
        print("   Step 3/3: Completing upload...")
        complete_response = requests.post(
            'https://slack.com/api/files.completeUploadExternal',
            headers={
                'Authorization': f'Bearer {bot_token}',
                'Content-Type': 'application/json'
            },
            json={
                'files': [
                    {
                        'id': file_id,
                        'title': f'AWS EC2 Report - {datetime.now().strftime("%Y-%m-%d")}'
                    }
                ],
                'channel_id': channel_id,
                'initial_comment': (
                    f"📊 *AWS EC2 Instance Report*\n"
                    f"• Total Instances: {total_instances}\n"
                    f"• Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"• Scan completed across all AWS regions"
                )
            },
            verify=True,  # Enforce SSL verification
            timeout=30    # Add timeout protection
        )

        complete_data = complete_response.json()
        if complete_data.get("ok"):
            print("✅ Report successfully uploaded to Slack!")
            
            # Get the file info if available
            files = complete_data.get("files", [])
            if files:
                file_url = files[0].get("permalink", "")
                if file_url:
                    print(f"   📎 View report at: {file_url}")
        else:
            error = complete_data.get('error')
            print(f"❌ Slack File Upload Error: {error}")
            
            # Provide specific error guidance
            if error == 'channel_not_found':
                print("   🔧 Solution: Check if the channel ID is correct and the bot is invited to the channel")
            elif error == 'invalid_auth':
                print("   🔧 Solution: Verify your bot token is valid and has files:write scope")
            elif error == 'not_in_channel':
                print("   🔧 Solution: Invite the bot to the channel using /invite @awsreportbot")
            elif error == 'missing_scope':
                print("   🔧 Solution: Add required scopes to your bot:")
                print("   🔧 Visit: https://api.slack.com/apps -> Your App -> OAuth & Permissions")
                print("   🔧 Required scopes: files:write, chat:write")
            
            # Try fallback method
            print("🔄 Trying summary-only approach...")
            send_report_summary_only(total_instances)

    except FileNotFoundError:
        print(f"\n❌ File not found: {filename}")
    except Exception as e:
        print(f"\n❌ Error uploading to Slack: {str(e)}")
        print("🔄 Trying summary-only approach...")
        send_report_summary_only(total_instances)

def send_report_summary_only(total_instances):
    """
    Alternative: Send only a summary message without file upload.
    Use this as a fallback if file upload continues to fail.
    """
    bot_token = os.environ.get('SLACK_BOT_TOKEN')
    channel_id = os.environ.get('SLACK_CHANNEL_ID')

    if not bot_token or not channel_id:
        print("\n⚠️ Slack integration is disabled - missing configuration")
        return

    try:
        print("\n📤 Sending report summary to Slack...")
        
        message = {
            "channel": channel_id,
            "text": (
                f"📊 *AWS EC2 Instance Report Generated*\n"
                f"• Total Instances Found: {total_instances}\n"
                f"• Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"• Report saved locally as Excel file\n"
                f"• Scanned all AWS regions for EC2 instances"
            )
        }
        
        response = requests.post(
            'https://slack.com/api/chat.postMessage',
            headers={
                'Authorization': f'Bearer {bot_token}',
                'Content-Type': 'application/json'
            },
            json=message,
            verify=True,  # Enforce SSL verification
            timeout=30    # Add timeout protection
        )
        
        response_data = response.json()
        if response_data.get("ok"):
            print("✅ Report summary sent to Slack!")
        else:
            print(f"❌ Failed to send summary: {response_data.get('error')}")
            
    except Exception as e:
        print(f"❌ Error sending summary to Slack: {str(e)}")

def test_channel_access():
    """Test if bot can access the specified channel"""
    bot_token = os.environ.get('SLACK_BOT_TOKEN')
    channel_id = os.environ.get('SLACK_CHANNEL_ID')
    
    print(f"\nTesting Slack channel access...")
    
    try:
        # Test API call
        response = requests.post(
            "https://slack.com/api/conversations.info",
            headers={"Authorization": f"Bearer {bot_token}"},
            data={"channel": channel_id},
            verify=True,  # Enforce SSL verification
            timeout=30    # Add timeout protection
        ).json()
        
        if response.get("ok"):
            channel_name = response.get("channel", {}).get("name")
            print(f"✅ Successfully connected to #{channel_name}")
            print(f"   Channel ID: {channel_id}")
            return True
        else:
            print(f"❌ Channel access failed: {response.get('error')}")
            print("   Make sure to:")
            print("   1. Invite the bot using: /invite @AWS_Report_Bot")
            print(f"   2. Verify channel ID: {channel_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing channel: {e}")
        return False

def validate_aws_permissions():
    """Validate AWS credentials have minimal required permissions"""
    try:
        # Test minimal EC2 permissions
        ec2 = boto3.client('ec2')
        ec2.describe_regions()
        print("✅ AWS permissions validated")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'UnauthorizedOperation':
            print("❌ Insufficient AWS permissions for EC2 operations")
            print("Required permissions: ec2:DescribeRegions, ec2:DescribeInstances")
            return False
        else:
            print(f"❌ AWS permission check failed: {e}")
            return False

if __name__ == '__main__':
    # Debug environment variables first
    debug_env_variables()
    
    # Show current AWS profile info
    show_current_profile_info()
    
    # Verify Slack token and test channel access
    if verify_slack_token():
        test_channel_access()
    
    # Check Slack configuration before starting the main process
    check_slack_configuration()
    
    # Your AWS credentials should be configured in your environment
    # (e.g., via `aws configure` or environment variables)
    print("🚀 Starting AWS EC2 Instance Discovery...")
    print("📋 This will generate a comprehensive Excel report with:")
    print("   • Instance details (ID, Name, Type, State)")
    print("   • IP addresses (Private & Public)")
    print("   • VPC and Subnet information")
    print("   • Security Groups and Launch Time")
    print("   • Regional and type summaries")
    print("\n" + "="*60)
    
    if not validate_aws_permissions():
        print("❌ Exiting due to insufficient AWS permissions")
        exit(1)

    list_instances_across_all_regions()