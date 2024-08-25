import discord
import json
from asyncio import sleep
from datetime import datetime
from main import adm

estoque = 'produtos.json'

def salvar_estoque(dados):
    with open(estoque, 'w') as arquivo:
        json.dump(dados, arquivo, indent=4)

def carregar_estoque():
    try:
        with open(estoque, 'r') as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

opcoes_de_compra = []
 


class menu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        produtos = carregar_estoque()
        opcoes_de_compra.clear()
        print(opcoes_de_compra)
        for chaves,valores in produtos.items():
            opcoes_de_compra.append(discord.SelectOption(label=chaves, value=chaves, description=f"Valor: R${valores['valor']} | Estoque: {valores['quantidade']}"))
            print(opcoes_de_compra)

    @discord.ui.select(placeholder="Selecione o produto que deseja adquirir",options=opcoes_de_compra, custom_id='opcoes')
    async def produtos(self, interact: discord.Interaction, select: discord.ui.Select):
        opcaoo = select.values[0]
        guild = interact.guild
        await interact.response.send_message(f'Canal de compras criado para ``{opcaoo}``', ephemeral=True)
            # Obtém a categoria específica para os canais
        category = discord.utils.get(guild.categories, name='🛒 ・ COMPRAS')
            # Define as permissões para o novo canal
        overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        interact.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        #role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
        channel = await guild.create_text_channel(opcaoo, category=category, overwrites=overwrites)
        comprador = interact.user.mention
        await channel.send(comprador)
        emb = discord.Embed(
            title=f"Compra de {opcaoo}",
            description=f'Bem vindo ao canal oficial de compras do {interact.guild.name}'

                        '\n\nTodos os responsáveis pela compra já estão cientes da abertura'
                        '\n\nEvite chamar alguém via DM, basta aguardar alguém já irá lhe atender...'
                                )
        await channel.send(embed=emb)
        view1 = botão_de_pix()
        view1.add_item(botão_de_venda().children[0])
        await channel.send(view=view1)

#função para carregar a mensagem salva
def load_message_and_channel_id():
    try:
        with open("fila1.txt", "r") as file:
            message_id = int(file.readline().strip())
            channel_id = int(file.readline().strip())
        return message_id, channel_id
    except FileNotFoundError:
        return None, None


class FormularioModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Formulário de Exemplo")

    # Adiciona os campos do formulário
    nome = discord.ui.TextInput(label="Nome", placeholder="Coloque o ID do comprador aqui ex:(1139973606680580206) ")
    prod =discord.ui.TextInput(label="Produto", placeholder="Digite o produto que ele adquiriu")
    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        mencao = f'<@{self.nome}>'
        category = discord.utils.get(guild.channels, name='🛒┃vendas-feitas') 
        hora = datetime.now()
        hora2 = hora.strftime('%H:%M | %d/%m/%y')
        produtos = carregar_estoque()
        rem = str(self.prod)

        message_id, channel_id = load_message_and_channel_id()    
        channel = guild.get_channel(channel_id)       
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await interaction.response.send_message('Mensagem não encontrada.', ephemeral=True)
            return

        try:
            if produtos[rem]['quantidade'] > 0:
                produtos[rem]['quantidade'] -= 1
                salvar_estoque(produtos)
                emb = discord.Embed(
                title=f"Compra finalizada ✅")
                
                emb.set_thumbnail(url=guild.icon)
                emb.add_field(name='', value=f'O usuário {mencao} realizou uma compra no servidor ',inline=False)
                emb.add_field(name='',value=f'Produto ``{self.prod}``',inline=False)
                emb.set_footer(text=f'Data - {hora2}')               
                view1 = menu()  
                await message.edit(view=view1) # atualiza a view com as quantidades dos produtos disponiveis
                await category.send(embed=emb)
                await interaction.response.send_message(f'Venda finalizada com sucesso e registrada em {category.mention}, esse canal será deletado em breve...', delete_after=5)
                await sleep(5)
                await interaction.channel.delete()
                
            else:
                await interaction.response.send_message('Você digitou um protudo com estoque zerado, atualize seus protudos')
        except:
            await interaction.response.send_message(f'Você digitou o produto errado verifique oque digitou -> ``{rem}``',ephemeral=True)

class botão_de_venda(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Finalizar venda', custom_id='finalizarvenda', style=discord.ButtonStyle.success)
    async def fim(self, interact: discord.Interaction, button):
        if interact.user.id != adm:
            await interact.channel.send(f'❌ Você não tem permissão para executar esta ação. Somente <@{adm}> pode finalizar')
            return
        await interact.response.send_modal(FormularioModal())

class botão_de_pix(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Chave Pix', custom_id='pix', style=discord.ButtonStyle.gray)
    async def fim(self, interact: discord.Interaction, button):
        if interact.user.id != adm:
            await interact.channel.send(f'❌ Você não tem permissão para executar esta ação. Somente <@{adm}> pode finalizar')
            return
        await interact.response.send_message(f'Chave pix de <@{adm}> \n ```SUA CHAVE```\n Após o pagamento enviar o comprovante aqui!')

 
