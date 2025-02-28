#!/usr/bin/env python3
import sys
import subprocess
import importlib

def check_dependencies():
    required_packages = ['aiohttp', 'colorama']
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            print(f"[!] {package} not installed. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            
check_dependencies()

import os
import sys
import asyncio
import aiohttp
from itertools import cycle
from colorama import Fore, Style, init
import shutil  # Added for terminal size support

init(autoreset=True)

# Set window title
if os.name == 'nt':
    os.system('title CHS - by c0h0s')

class TurboWebhookSpammer:
    def __init__(self):
        self.session = None
        self.active = True
        self.print_header()
        
    def print_header(self):
        self.clear_screen()
        # Get terminal size for centering
        term_size = shutil.get_terminal_size((80, 20))
        columns = term_size.columns
        rows = term_size.lines

        # ASCII art lines for header
        header_lines = [
            " ▄████▄   ██░ ██   ██████ ",
            "▒██▀ ▀█  ▓██░ ██▒▒██    ▒ ",
            "▒▓█    ▄ ▒██▀▀██░░ ▓██▄   ",
            "▒▓▓▄ ▄██▒░▓█ ░██   ▒   ██▒",
            "▒ ▓███▀ ░░▓█▒░██▓▒██████▒▒",
            "░ ░▒ ▒  ░ ▒ ░░▒░▒▒ ▒▓▒ ▒ ░",
            "  ░  ▒    ▒ ░▒░ ░░ ░▒  ░ ░",
            "░         ░  ░░ ░░  ░  ░  ",
            "░ ░       ░  ░  ░      ░  ",
            "░                         "
        ]
        # Calculate vertical padding
        header_height = len(header_lines) + 2  # including the version line
        vertical_padding = max((rows - header_height) // 2, 0)
        print("\n" * vertical_padding, end="")

        # Print ASCII art centered horizontally in red
        for line in header_lines:
            print(Fore.RED + line.center(columns) + Style.RESET_ALL)
        
        # Print tool version centered horizontally in yellow
        version_line = "Webhook Spam Tool v1.2"
        print(Fore.YELLOW + version_line.center(columns) + Style.RESET_ALL + "\n")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    async def get_input(self, prompt):
        return input(f"{Fore.BLUE}[>]{Style.RESET_ALL} {prompt}: ").strip()

    async def validate_webhook(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url) as response:
                    return response.status in (200, 204)
        except Exception:
            return False

    async def delete_webhook(self, url):
        try:
            async with self.session.delete(url) as response:
                if response.status == 204:
                    print(f"{Fore.GREEN}[✓]{Style.RESET_ALL} Webhook deleted!")
                else:
                    print(f"{Fore.RED}[X]{Style.RESET_ALL} Failed to delete webhook")
        except Exception as e:
            print(f"{Fore.RED}[!]{Style.RESET_ALL} Error: {str(e)}")

    async def send_message(self, url, message):
        try:
            async with self.session.post(url, json={"content": message}) as response:
                if response.status == 204:
                    return True
                elif response.status == 429:
                    retry_after = (await response.json()).get('retry_after', 1)
                    print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} Rate limited! Waiting {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return False
                return False
        except Exception as e:
            print(f"{Fore.RED}[!]{Style.RESET_ALL} Error: {str(e)}")
            return False

    async def spam_webhook(self):
        self.print_header()
        webhook_url = await self.get_input("Enter webhook URL")
        if not await self.validate_webhook(webhook_url):
            print(f"{Fore.RED}[!]{Style.RESET_ALL} Invalid webhook URL")
            return

        message = await self.get_input("Enter message")
        include_server = (await self.get_input("Include server link? (y/n)")).lower() == 'y'
        server_url = ""
        if include_server:
            server_url = await self.get_input("Enter server URL")
        
        auto_mention = (await self.get_input("Add @everyone @here? (y/n)")).lower() == 'y'
        
        amount = int(await self.get_input("Number of messages"))
        delay = float(await self.get_input("Delay between messages (ms)")) / 1000

        messages = [message]
        if include_server:
            messages.append(server_url)
        message_cycle = cycle(messages)

        self.session = aiohttp.ClientSession()

        print(f"\n{Fore.YELLOW}[!]{Style.RESET_ALL} Starting spam...\n")

        try:
            sent_count = 0
            while sent_count < amount:
                base_message = next(message_cycle)
                final_message = f"@everyone @here {base_message}" if auto_mention else base_message
                
                success = await self.send_message(webhook_url, final_message)
                if success:
                    sent_count += 1
                    print(f"{Fore.GREEN}[✓]{Style.RESET_ALL} Message {sent_count}/{amount} sent")
                await asyncio.sleep(delay)

            if (await self.get_input("Delete webhook? (y/n)")).lower() == 'y':
                await self.delete_webhook(webhook_url)

        except Exception as e:
            print(f"{Fore.RED}[!]{Style.RESET_ALL} Critical error: {str(e)}")
        finally:
            await self.session.close()
        input("\nPress Enter to continue...")

    async def main(self):
        while self.active:
            try:
                self.print_header()
                print(f"    {Fore.GREEN}[1]{Style.RESET_ALL} Start Spam Attack")
                print(f"    {Fore.RED}[2]{Style.RESET_ALL} Exit Program\n")
                
                choice = await self.get_input("Select option")
                
                if choice == "1":
                    await self.spam_webhook()
                elif choice == "2":
                    print(f"\n{Fore.RED}[!]{Style.RESET_ALL} Exiting...")
                    self.active = False
                    sys.exit(0)
                else:
                    print(f"{Fore.RED}[!]{Style.RESET_ALL} Invalid option!")
                    await asyncio.sleep(1)

            except KeyboardInterrupt:
                print(f"\n{Fore.RED}[!]{Style.RESET_ALL} Operation cancelled!")
                self.active = False
                sys.exit(0)

if __name__ == "__main__":
    tool = TurboWebhookSpammer()
    asyncio.run(tool.main())
