import discord
from discord.ext import commands
import pandas as pd
import re
import requests
from io import BytesIO
from collections import defaultdict
import os
from dotenv import load_dotenv

# Načítanie .env súboru s tokenom
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

CSV_URL = os.getenv("CSV_URL")

def get_dataframe():
    response = requests.get(CSV_URL, timeout=10)
    response.raise_for_status()
    return pd.read_csv(BytesIO(response.content), encoding='utf-8-sig')

def extract_first_number(text):
    if pd.isna(text):
        return 0
    match = re.match(r'^(\d+)', str(text).strip())
    return int(match.group(1)) if match else 0

@bot.command()
async def zl(ctx):
    try:
        df = get_dataframe()
    except Exception as e:
        await ctx.send(f"Chyba pri sťahovaní alebo čítaní dát: {e}")
        return

    names = pd.concat([df.iloc[2:31, 8], df.iloc[34:63, 8]])
    zl = pd.concat([df.iloc[2:31, 10], df.iloc[34:63, 10]])

    sum_zl = 0
    players_zl = []

    for name, zl_val in zip(names, zl):
        zl_number = extract_first_number(zl_val)
        if zl_number > 0 and pd.notna(name):
            sum_zl += zl_number
            players_zl.append(f"{name} ({zl_number})")

    result = f"**Súčet zl:** {sum_zl}\n**Hráči:**\n" + "\n".join(f"- {p}" for p in players_zl)
    await ctx.send(result)

@bot.command()
async def bir(ctx):
    try:
        df = get_dataframe()
    except Exception as e:
        await ctx.send(f"Chyba pri sťahovaní alebo čítaní dát: {e}")
        return

    names = pd.concat([df.iloc[2:31, 8], df.iloc[34:63, 8]])
    bir = pd.concat([df.iloc[2:31, 11], df.iloc[34:63, 11]])

    sum_bir = 0
    players_bir = []

    for name, bir_val in zip(names, bir):
        try:
            bir_number = int(bir_val)
        except (ValueError, TypeError):
            bir_number = 0
        if bir_number > 0 and pd.notna(name):
            sum_bir += bir_number
            players_bir.append(f"{name} ({bir_number})")

    result = f"**Súčet bir:** {sum_bir}\n**Hráči:**\n" + "\n".join(f"- {p}" for p in players_bir)
    await ctx.send(result)

@bot.command()
async def letka(ctx):
    try:
        df = get_dataframe()
    except Exception as e:
        await ctx.send(f"Chyba pri sťahovaní alebo čítaní dát: {e}")
        return

    names = pd.concat([df.iloc[2:31, 8], df.iloc[34:63, 8]])
    letka = pd.concat([df.iloc[2:31, 12], df.iloc[34:63, 12]])

    # Mapa písmen na celé názvy
    letter_to_name = {
        'h': 'Harpie',
        'v': 'Vtáky',
        'm': 'Manty',
        'l': 'Ladony'
    }

    sums = {name: 0 for name in letter_to_name.values()}
    owners = defaultdict(list)
    skipped = []

    for name, value in zip(names, letka):
        if pd.isna(value) or pd.isna(name):
            continue
        match = re.match(r'^(\d+)?([hvmlHVML])', str(value).strip())
        if match:
            number = int(match.group(1)) if match.group(1) else 0
            letter = match.group(2).lower()
            full_name = letter_to_name.get(letter)
            if full_name:
                sums[full_name] += number
                owners[full_name].append(f"{name} ({number})")
        else:
            skipped.append(f"{name}: {value}")

    result = "**Letka súčty:**"
    for name in ["Harpie", "Vtáky", "Manty", "Ladony"]:
        result += f"{name}: {sums[name]}\n"
        if owners[name]:
            result += "".join(f" - {p}\n" for p in owners[name])

    if skipped:
        result += "\n**Preskočené hodnoty:**\n" + "\n".join(f" - {val}" for val in skipped)

    await ctx.send(result)


# Spustenie bota
bot.run(os.getenv("DISCORD_TOKEN"))
