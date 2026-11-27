import discord, json, os
from discord.ext import commands
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from flask import Flask
from threading import Thread
import math

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot online!")
    def log_message(self, *args):
        pass

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

Thread(target=keep_alive, daemon=True).start()




# =========================
# SISTEMA DE WARNS
# =========================

ARQUIVO_WARNS = "warns.json"


def carregar_warns():
    try:
        with open(ARQUIVO_WARNS, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    except FileNotFoundError:
        return {}


def salvar_warns(warns):
    with open(ARQUIVO_WARNS, "w", encoding="utf-8") as arquivo:
        json.dump(warns, arquivo, indent=4, ensure_ascii=False)


warns = carregar_warns()

# =========================
# CONFIGURAÇÃO
# =========================

ARQUIVO_CARGOS = "cargos_anteriores.json"


def carregar_cargos():
    try:
        with open(
            ARQUIVO_CARGOS,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(arquivo)

    except FileNotFoundError:
        return {}


def salvar_cargos(cargos):
    with open(
        ARQUIVO_CARGOS,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            cargos,
            arquivo,
            indent=4
        )


cargos_anteriores = carregar_cargos()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
MEU_ID = 1536894356450185256
bot = commands.Bot(
    command_prefix="?",
    intents=intents,
    help_command=None
)

# Impede o console de ser iniciado várias vezes
console_iniciado = False


# =========================
# BOT ONLINE
# =========================

@bot.event
async def on_ready():
    global console_iniciado

    print("================================")
    print(f"BOT ONLINE: {bot.user}")
    print("Bot de moderação iniciado!")
    print("O bot acordou! 🥱➡️🤖")
    print("================================")

    canal = discord.utils.get(
        bot.get_all_channels(),
        name="bate-papo"  
    )
        
# =======================
# WARN
# =======================

@bot.command()
@commands.has_permissions(moderate_members=True)
async def warn(ctx, membro: discord.Member, *, motivo="Nenhum motivo informado"):

    servidor = str(ctx.guild.id)
    usuario = str(membro.id)

    if servidor not in warns:
        warns[servidor] = {}

    if usuario not in warns[servidor]:
        warns[servidor][usuario] = []

    warns[servidor][usuario].append(motivo)

    salvar_warns(warns)

    quantidade = len(warns[servidor][usuario])

    await ctx.send(
        f"⚠️ {membro.mention} recebeu um warn!\n"
        f"📝 Motivo: **{motivo}**\n"
        f"📊 Total de warns: **{quantidade}**"
    )
# =======================
# VER WARNS
# =======================
@bot.command()
async def verwarns(ctx, membro: discord.Member):

    servidor = str(ctx.guild.id)
    usuario = str(membro.id)

    lista = warns.get(servidor, {}).get(usuario, [])

    if not lista:
        await ctx.send(
            f"✅ {membro.mention} não possui warns."
        )
        return

    texto = ""

    for i, motivo in enumerate(lista, 1):
        texto += f"**{i}.** {motivo}\n"

    embed = discord.Embed(
        title=f"⚠️ Warns de {membro}",
        description=texto,
        color=discord.Color.orange()
    )

    embed.set_footer(
        text=f"Total: {len(lista)}"
    )

    await ctx.send(embed=embed)
    
# =======================
# REMOVER WARN
# =======================
    
@bot.command()
@commands.has_permissions(moderate_members=True)
async def unwarn(ctx, membro: discord.Member, numero: int):

    servidor = str(ctx.guild.id)
    usuario = str(membro.id)

    lista = warns.get(servidor, {}).get(usuario, [])

    if numero < 1 or numero > len(lista):
        await ctx.send("❌ Esse warn não existe.")
        return

    motivo = lista.pop(numero - 1)

    salvar_warns(warns)

    await ctx.send(
        f"✅ Warn **#{numero}** removido de {membro.mention}.\n"
        f"📝 Motivo antigo: **{motivo}**"
    )

# =========================
# REGRAS
# =========================

@bot.command()
async def regras(ctx):

    embed = discord.Embed(
        title="📜 Regras do servidor",
        description=(
            "1️⃣ Desrespeite os outros membros.\n"
            "2️⃣ Não faça spam.\n"
            "3️⃣ Não divulgue coisas sem permissão.\n"
            "4️⃣ Envie conteúdo +18.\n"
            "5️⃣ Desrespeite a equipe de administração."
        ),
        color=discord.Color.white()
    )

    await ctx.send(embed=embed)


# =========================
# KICK
# =========================

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(
    ctx,
    membro: discord.Member,
    *,
    motivo="Nenhum motivo informado"
):

    await membro.kick(reason=motivo)

    await ctx.send(
        f"👢 **{membro}** foi expulso.\n"
        f"📝 Motivo: {motivo}"
    )


# =========================
# BAN
# =========================

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(
    ctx,
    membro: discord.Member,
    *,
    motivo="Nenhum motivo informado"
):

    await membro.ban(reason=motivo)

    await ctx.send(
        f"🔨 **{membro}** foi banido.\n"
        f"📝 Motivo: {motivo}"
    )


# =========================
# UNBAN
# =========================

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, nome):

    banidos = [
        entry async for entry in ctx.guild.bans()
    ]

    for entry in banidos:

        usuario = entry.user

        if str(usuario) == nome:

            await ctx.guild.unban(usuario)

            await ctx.send(
                f"✅ **{usuario}** foi desbanido."
            )

            return

    await ctx.send(
        "❌ Não encontrei esse usuário na lista de banidos."
    )


# =========================
# LIMPAR MENSAGENS
# =========================

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, quantidade: int):

    if quantidade <= 0:
        await ctx.send(
            "❌ A quantidade precisa ser maior que 0."
        )
        return

    apagadas = await ctx.channel.purge(
        limit=quantidade + 1
    )

    mensagem = await ctx.send(
        f"🧹 Apaguei **{len(apagadas) - 1} mensagens**."
    )

    await mensagem.delete(delay=3)


# =========================
# MUTE
# =========================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, membro: discord.Member):

    guild = ctx.guild

    cargo = discord.utils.get(
        guild.roles,
        name="Muted"
    )

    if cargo is None:

        cargo = await guild.create_role(
            name="Muted"
        )

        for canal in guild.channels:

            try:

                await canal.set_permissions(
                    cargo,
                    send_messages=False,
                    speak=False
                )

            except discord.Forbidden:
                pass

    await membro.add_roles(cargo)

    await ctx.send(
        f"🔇 **{membro}** foi silenciado."
    )


# =========================
# UNMUTE
# =========================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, membro: discord.Member):

    cargo = discord.utils.get(
        ctx.guild.roles,
        name="Muted"
    )

    if cargo is None:

        await ctx.send(
            "❌ O cargo `Muted` não existe."
        )

        return

    await membro.remove_roles(cargo)

    await ctx.send(
        f"🔊 **{membro}** foi dessilenciado."
    )

# =========================
# HELP
# =========================
@bot.command(name="ajuda")
async def help(ctx):
    embed = discord.Embed(
        title =" ¿ Ajuda ?",
        description=(
            "`Cargos` → Adm → Bot → Mod → Membro → Mudo → Castigado\n"
            "`Tempo no ?cargotemp` → S = seg;M = min;H = horas;D = dias"
        ),
        color=discord.Color.blue()
    )
    
    await ctx.send(embed=embed)
#==========================
#VERSÃO
#==========================
@bot.command()
async def v(ctx):
    embed = discord.Embed(
        title =" Verção 0.1.5.5",
        description=(
            "`Novidades` → Adicionado ?pesquisa ; Bot cadastrado na nuvem,sem dormir ; Calculadora Cientifica integrada"
            
        ),
        color=discord.Color.red()
    )
    
    await ctx.send(embed=embed)
    
# =========================
# COMANDOS
# =========================

@bot.command()
async def comandos(ctx):

    embed = discord.Embed(
        title="🤖 Comandos de moderação",
        description=(
            "`?regras` → Mostra as regras\n"
            "`?kick @usuário` → Expulsa alguém\n"
            "`?ban @usuário motivo` → Bane alguém\n"
            "`?unban nome#0000` → Desbane alguém\n"
            "`?clear 10` → Apaga mensagens\n"
            "`?mute @usuário` → Silencia alguém\n"
            "`?unmute @usuário` → Remove o silêncio\n"
            "`?castigo @usuário` → Coloca alguém de castigo\n"
            "`?tirarcastigo @usuário` → Tira o castigo de alguém\n"
            "`?darcargo @usuário cargo` → Dá um cargo a alguém\n"
            "`?tirarcargo` → Tira o cargo de alguém\n"
            "`?meu_id` → Mostra seu ID\n"
            "`?cargotemp @usuário cargo tempo` → Dá um cargo temporario a alguém\n"
            "`?ajuda` → Explica mais algumas funções\n"
            "`?v` → Ver versão do bot\n"
            "`?warn @usuário motivo` → Dá um aviso a alguém\n"
            "`?unwarn @usuário num` → Tira um aviso de alguém\n"
            "`?verwarns @usuário` → Vê os warns(avisos) de alguém\n"
            "`?pesquisa assunto` → O bot faz uma pesquisa/resumo do assunto"
            
        ),
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)


# =========================
# ERROS
# =========================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send(
            "🚫 Você não tem permissão para usar esse comando."
        )

    elif isinstance(error, commands.MissingRequiredArgument):

        await ctx.send(
            "❌ Está faltando algum argumento."
        )

    elif isinstance(error, commands.MemberNotFound):

        await ctx.send(
            "❌ Não encontrei esse membro."
        )

    elif isinstance(error, commands.MissingRole):

        await ctx.send(
            "❌ Você não possui o cargo necessário."
        )

    elif isinstance(error, commands.CommandNotFound):

        pass

    else:

        print(f"Erro: {error}")

# =========================
# SORTEIO
# =========================


# =========================
# RESPOSTAS AUTOMÁTICAS
# =========================
@bot.event
async def on_message(message):
    usuario = message.guild.get_member(MEU_ID)
    
    # Ignora mensagens de bots
    if message.author.bot:
        return

    texto = message.content.lower()

    # =========================
    # RESPOSTAS NORMAIS
    # =========================

    if texto == "oi":
        await message.channel.send(
            f"Opa, {message.author.mention}! Tudo certo?Quantos chifres você levou hoje?"
        )

    elif texto in ("olá", "ola"):
        await message.channel.send(
            "Olá! Seja bem-vindo para o clube dos cornos!"
        )

    elif texto == "bom dia":
        await message.channel.send(
            "Bom dia,acordo agora kkkkkkk "
        )

    elif texto == "boa noite":
        await message.channel.send(
            "Boa noite,não vai dormi tarde seu merdinha "
        )

    elif texto == "tchau":
        await message.channel.send(
            "Sayonara seu bosta"
        )
    elif texto in ("qm q te criou","quem te criou","quem que te criou","quem q te criou","qm te criou?","qm q te criou?","quem te criou?","quem que te criou?","quem q te criou?","qm te criou?"):
        await message.channel.send(
            "O "
            f"{usuario.mention} "
            "que me criou."
        )

    # -------------------------
    # QUANDO RESPONDEM AO BOT
    # -------------------------

    if message.reference is not None:

        try:

            mensagem_original = await message.channel.fetch_message(
                message.reference.message_id
            )

            if mensagem_original.author == bot.user:

                await message.channel.send(
                    f"Para de me responder, "
                    f"{message.author.mention} :)"
                )

        except (
            discord.NotFound,
            discord.Forbidden
        ):
            pass

    # Mantém os comandos funcionando
    await bot.process_commands(message)


# =========================
# DAR CASTIGO
# =========================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def castigo(ctx, membro: discord.Member):

    cargo_castigado = discord.utils.get(
        ctx.guild.roles,
        name="Castigado"
    )

    if cargo_castigado is None:
        cargo_castigado = await ctx.guild.create_role(
            name="Castigado"
        )

    # Guarda os IDs dos cargos atuais
    cargos_anteriores[str(membro.id)] = [
        cargo.id
        for cargo in membro.roles
        if cargo != ctx.guild.default_role
        and cargo != cargo_castigado
    ]

    salvar_cargos(cargos_anteriores)

    # Remove os cargos antigos
    for cargo in membro.roles:

        if cargo != ctx.guild.default_role:
            try:
                await membro.remove_roles(cargo)
            except discord.Forbidden:
                pass

    # Coloca Castigado
    await membro.add_roles(cargo_castigado)

    await ctx.send(
        f"🔨 {membro.mention} foi colocado de castigo!"
    )

# =========================
# TIRAR CASTIGO
# =========================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def tirarcastigo(ctx, membro: discord.Member):

    cargo_castigado = discord.utils.get(
        ctx.guild.roles,
        name="Castigado"
    )

    if cargo_castigado is None:
        await ctx.send(
            "❌ O cargo `Castigado` não existe."
        )
        return

    usuario_id = str(membro.id)

    if usuario_id not in cargos_anteriores:
        await ctx.send(
            "❌ Não encontrei os cargos anteriores desse usuário."
        )
        return

    # Remove Castigado
    await membro.remove_roles(cargo_castigado)

    # Recupera os IDs
    ids = cargos_anteriores[usuario_id]

    cargos_para_restaurar = []

    for cargo_id in ids:

        cargo = ctx.guild.get_role(cargo_id)

        if cargo is not None:
            cargos_para_restaurar.append(cargo)

    # Restaura
    if cargos_para_restaurar:
        await membro.add_roles(
            *cargos_para_restaurar
        )

    # Apaga o registro
    del cargos_anteriores[usuario_id]

    salvar_cargos(cargos_anteriores)

    await ctx.send(
        f"✅ Os cargos de {membro.mention} "
        f"foram restaurados!"
    )

# =========================
# DAR CARGO
# =========================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def darcargo(ctx, membro: discord.Member, *, nome_cargo):

    cargo = discord.utils.get(
        ctx.guild.roles,
        name=nome_cargo
    )

    if cargo is None:
        await ctx.send(
            f"❌ Não encontrei o cargo **{nome_cargo}**."
        )
        return

    # Cargo mais alto do bot
    if cargo >= ctx.guild.me.top_role:
        await ctx.send(
            "❌ Não posso dar esse cargo.\n"
            "O cargo precisa estar abaixo do meu cargo."
        )
        return

    try:
        await membro.add_roles(
            cargo,
            reason=f"Cargo dado por {ctx.author}"
        )

        await ctx.send(
            f"✅ {membro.mention} recebeu o cargo "
            f"**{cargo.name}**!"
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Não tenho permissão para dar esse cargo."
        )


# =========================
# REMOVER CARGO
# =========================

@bot.command()
@commands.has_permissions(manage_roles=True)
async def removercargo(
    ctx,
    membro: discord.Member,
    *,
    nome_cargo
):

    cargo = discord.utils.get(
        ctx.guild.roles,
        name=nome_cargo
    )

    if cargo is None:
        await ctx.send(
            f"❌ Não encontrei o cargo **{nome_cargo}**."
        )
        return

    if cargo >= ctx.guild.me.top_role:
        await ctx.send(
            "❌ Não posso remover esse cargo.\n"
            "O cargo precisa estar abaixo do meu cargo."
        )
        return

    if cargo not in membro.roles:
        await ctx.send(
            f"⚠️ {membro.mention} não possui "
            f"o cargo **{cargo.name}**."
        )
        return

    try:
        await membro.remove_roles(
            cargo,
            reason=f"Cargo removido por {ctx.author}"
        )

        await ctx.send(
            f"✅ O cargo **{cargo.name}** foi removido "
            f"de {membro.mention}!"
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Não tenho permissão para remover esse cargo."
        )
# ===========================
# ID DO USUARIO
# ===========================
@bot.command()
async def meu_id(ctx):
    await ctx.send(f"Seu ID é: `{ctx.author.id}`")

# =========================
# CARGO TEMPORÁRIO
# =========================

def converter_tempo(tempo):

    match = re.fullmatch(
        r"(\d+)(s|m|h|d)",
        tempo.lower()
    )

    if not match:
        return None

    numero = int(match.group(1))
    unidade = match.group(2)

    if unidade == "s":
        return numero

    elif unidade == "m":
        return numero * 60

    elif unidade == "h":
        return numero * 60 * 60

    elif unidade == "d":
        return numero * 60 * 60 * 24


@bot.command()
@commands.has_permissions(manage_roles=True)
async def cargotemp(
    ctx,
    membro: discord.Member,
    nome_cargo: str,
    tempo: str
):

    guild = ctx.guild

    # Procura o cargo
    cargo = discord.utils.get(
        guild.roles,
        name=nome_cargo
    )

    if cargo is None:
        await ctx.send(
            f"❌ Não encontrei o cargo **{nome_cargo}**."
        )
        return

    # Converte o tempo
    segundos = converter_tempo(tempo)

    if segundos is None:
        await ctx.send(
            "❌ Tempo inválido!\n\n"
            "Use:\n"
            "`10s` → 10 segundos\n"
            "`10m` → 10 minutos\n"
            "`2h` → 2 horas\n"
            "`1d` → 1 dia"
        )
        return

    # Verifica hierarquia do bot
    if cargo >= guild.me.top_role:
        await ctx.send(
            "❌ Não posso usar esse cargo.\n"
            "Coloque o cargo abaixo do cargo do bot."
        )
        return

    if membro.top_role >= guild.me.top_role:
        await ctx.send(
            "❌ Não posso modificar esse usuário."
        )
        return

    # Guarda os cargos antigos
    cargos_antigos = [
        r for r in membro.roles
        if r != guild.default_role
    ]

    try:

        # Remove os cargos antigos
        if cargos_antigos:
            await membro.remove_roles(
                *cargos_antigos,
                reason="Cargo temporário"
            )

        # Coloca o cargo temporário
        await membro.add_roles(
            cargo,
            reason="Cargo temporário"
        )

        await ctx.send(
            f"⏱️ {membro.mention} recebeu o cargo "
            f"**{cargo.name}** por **{tempo}**."
        )

        # Espera o tempo
        await asyncio.sleep(segundos)

        # Remove o cargo temporário
        await membro.remove_roles(
            cargo,
            reason="Tempo do cargo temporário acabou"
        )

        # Restaura os cargos antigos
        cargos_validos = [
            r for r in cargos_antigos
            if r in guild.roles
            and r < guild.me.top_role
        ]

        if cargos_validos:
            await membro.add_roles(
                *cargos_validos,
                reason="Restaurando cargos antigos"
            )

        await ctx.send(
            f"✅ O tempo de **{cargo.name}** de "
            f"{membro.mention} acabou. "
            f"Os cargos anteriores foram restaurados!"
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Não tenho permissão para modificar os cargos."
        )

#=============================
#     PESQUISA
#=============================

@bot.command(name="pesquisa")
async def pesquisa(ctx, *, assunto=None):
    if not assunto:
        await ctx.send("Uso certo: `?pesquisa cachorro`")
        return

    try:
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{assunto}"
        r = requests.get(url, headers={"User-Agent": "DiscordBot"}, timeout=10)
        data = r.json()

        if "extract" not in data:
            await ctx.send(f"Não achei nada sobre **{assunto}**")
            return

        titulo = data.get("title", assunto)
        resumo = data.get("extract", "")[:900]
        link = data.get("content_urls", {}).get("desktop", {}).get("page", "")

        await ctx.send(f"**{titulo}**\n\n{resumo}...\n\n🔗 {link}")

    except Exception as e:
        await ctx.send("Deu erro na pesquisa, tenta de novo.")

#=======================
#MONITOR 24h
#=======================

app = Flask('')

@app.route('/')
def home():
    return "Bot online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

#==========================
#CALCULADORA CIENTIFICA
#==========================
@bot.command()
async def calc(ctx, *, conta: str = None):
    if conta is None:
        await ctx.send("Manda a conta! Exemplo: `?calc 2+2*3` ou `?calc sqrt(144)`")
        return

    try:
        # Deixa a conta mais fácil de digitar
        conta_limpa = conta.lower().replace('^', '**').replace('x', '*').replace(',', '.').replace('÷', '/').replace('²','**2').replace('³','**3')

        # Funções liberadas
        funcoes = {
            'sin': lambda x: math.sin(math.radians(x)),
            'cos': lambda x: math.cos(math.radians(x)),
            'tan': lambda x: math.tan(math.radians(x)),
            'sqrt': math.sqrt,
            'log': math.log10,
            'ln': math.log,
            'abs': abs,
            'pi': math.pi,
            'e': math.e,
        }

        resultado = eval(conta_limpa, {"__builtins__": {}}, funcoes)

        await ctx.send(f"`{conta}` = **{resultado}**")

    except Exception as e:
        await ctx.send(f"Deu erro nessa conta.Tenta de novo. Ex: `?calc (2+3)*4`")

@bot.command()
async def c(ctx, *, conta: str = None):
    # Atalho pra ?calc, só pra ser mais rápido
    await ctx.invoke(bot.get_command('calc'), conta=conta)
    
# =========================
# TOKEN
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
