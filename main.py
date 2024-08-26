import discord
from discord import app_commands
from datetime import datetime
from discord.ext import commands
from Store.store import menu, carregar_estoque,salvar_estoque,botão_de_venda,botão_de_pix

class bot_on(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='>', intents=discord.Intents.all())
    
    async def setup_hook(self):
        self.add_view(menu())
        self.add_view(botão_de_venda())
        self.add_view(botão_de_pix())
        #ativa todas as views quando o bot inicia 
    
adm = #colocar o id do dono 


bot = bot_on()

@bot.command()
async def vendas(ctx: commands.Context):
    embed = discord.Embed(
        title='🛒 STORE 🛒',
        description=f'Veja os produtos disponíveis abaixo e escolha a compra de acordo com a necessidade.',
        colour=discord.Colour(5763719),
    )
    embed.set_thumbnail(url=ctx.guild.icon) 
    view1 = menu()
    await ctx.channel.purge(limit=1)
    mensagem = await ctx.channel.send(embed=embed, view=view1)
    with open("vendas.txt", "w") as file: 
        file.write(f"{mensagem.id}\n{ctx.channel.id}")
        #salva o id do canal e da mensagem para editar depois

#função para carregar a mensagem salva
def load_message_and_channel_id():
    try:
        with open("vendas.txt", "r") as file:
            message_id = int(file.readline().strip())
            channel_id = int(file.readline().strip())
        return message_id, channel_id
    except FileNotFoundError:
        return None, None


@bot.tree.command(name="adicionar", description="Adicionar produto no estoque")
@app_commands.describe(produto="Nome do produto", valor="Valor", quantidade="Quantidade")
async def adicionar(interaction: discord.Interaction, produto: str, valor: int, quantidade: int):
    if interaction.user.id != adm:
        await interaction.response.send_message(
            f'❌ Você não tem permissão para executar esta ação. Somente <@{adm}> pode adicionar produtos.',
            ephemeral=True
        )
        return
    estoque = carregar_estoque()
    
    if produto not in estoque:
        #procura o produto informado no tree comand, se não estiver na lista adiciona o produto e salva
        estoque[produto] = {'valor': valor, 'quantidade': quantidade}
        salvar_estoque(estoque)
        await interaction.response.send_message('Produto adicionado', ephemeral=True)
        message_id, channel_id = load_message_and_channel_id()
        channel = interaction.guild.get_channel(channel_id)
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await interaction.response.send_message('Mensagem não encontrada.', ephemeral=True)
            return
        view1 = menu()
        await message.edit(view=view1)
    else:
        await interaction.response.send_message('Produto já existe no estoque.', ephemeral=True)

@bot.tree.command(name="remover", description="Remove um protudo do estoque")
@app_commands.describe(produto="Nome do produto")
async def remover(interaction: discord.Interaction, produto: str):
    if interaction.user.id != adm:
        await interaction.response.send_message(
            f'❌ Você não tem permissão para executar esta ação. Somente <@{adm}> pode remover produtos.',
            ephemeral=True
        )
        return
    estoque = carregar_estoque()
    #procura o produto informado no tree comand, exclui da lista de produtos e salva
    if produto in estoque:
        del estoque[produto]
        salvar_estoque(estoque)   
        await interaction.response.send_message('Produto removido', ephemeral=True)
        message_id, channel_id = load_message_and_channel_id()
        channel = interaction.guild.get_channel(channel_id)       
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await interaction.response.send_message('Mensagem não encontrada.', ephemeral=True)
            return
        view1 = menu()
        await message.edit(view=view1)
        #edita a barra de opções de compra
    else:
        await interaction.response.send_message('Produto não encontrado no estoque.', ephemeral=True)    



@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')

bot.run('token aqui')
