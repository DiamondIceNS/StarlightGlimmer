STRINGS = {
    # General messages
    "bot.alert_update": "Eu atualizei para a versão **{0}**! Confira a página de ajuda de comandos para os novos comandos digite `{1}help`, ou visite https://github.com/DiamondIceNS/StarlightGlimmer/releases para o changelog completo.",
    "bot.description":
        """Oi! Eu sou a {0}! Estou aqui para ajudar a coordenar pixel art em sites de colocação de pixels.
        Eu tenho recursos como visualização de tela e verificação de templates que certamente serão úteis.
        Vamos começar a pintar pixels!""",
    "bot.help_ending_note": "Digite '{0}{1} <command>' para mais informações do comando.",
    "bot.ping": "Pinging...",
    "bot.pong": "Pong! | **{0}ms**",
    "bot.suggest": "Sua sugestão foi enviada. Obrigado por sua contribuição!",
    "bot.version": "O numero da minha versão é **{0}**",

    # Animotes messages
    "animotes.guild_opt_in": "O compartilhamento de emojis foi **ativado** para essa guild.",
    "animotes.guild_opt_out": "O compartilhamento de emojis foi **desativado** para esta guild.",
    "animotes.member_opt_in": "Você optou com sucesso em **aceitar** a conversão de emojis.",
    "animotes.member_opt_out": "Você cancelou ** com êxito ** a conversão de emojis.",

    # Canvas messages
    "render.diff": "{0}/{1} | {2} erros | {3:.2f}% completo",
    "render.diff_bad_color": "{0}/{1} | {2} erros | {3} cores erradas | {4:.2f}% completo",
    "render.large_template": "(Processando template grande, isso pode levar alguns segundos ...)",
    "render.quantize": "Convertidos {0} pixels.",
    "render.repeat_not_found": "Não foi possível encontrar um comando válido para repetir.",

    # Configuration messages
    "configuration.alert_channel_cleared": "O canal de Alerta foi desabilitado.",
    "configuration.alert_channel_set": "O canal de Alerta foi definido para {0}.",
    "configuration.autoscan_disabled": "Autoscan foi desativado.",
    "configuration.autoscan_enabled": "Autoscan foi ativado.",
    "configuration.canvas_check": "O canvas padrão desta guild é **{0}**.\n"
                                  "Para alterar o canvas padrão, execute este comando novamente com um canvas suportado. (Use `{1}help canvas` para ver uma lista.)",
    "configuration.canvas_set": "O canvas padrão foi definido para **{0}**.",
    "configuration.language_check": "O idioma atual deste guild é **{1}**.\n"
                                    "Para definir um novo idioma, execute este comando novamente com uma das seguintes opções:\n"
                                    "```{0}```",
    "configuration.language_set": "O idioma foi definido para **Português (BR)**.",
    "configuration.prefix_set": "O prefixo deste server foi definido para **{0}**.",

    # Error messages
    "bot.error.bad_png": "Esta imagem parece estar corrompida. Tente salvá-la novamente com um editor de imagens ou usando `{0}{1}`.",
    "bot.error.command_on_cooldown": "Esse comando está em cooldown. Tente novamente em {0:.01f}s.",
    "bot.error.missing_attachment": "Esse comando requer um anexo.",
    "bot.error.no_canvas": "Esse comando requer um subcomando.",
    "bot.error.no_permission": "Você não tem permissão para usar esse comando.",
    "bot.error.no_png": "Esse comando requer uma imagem PNG.",
    "bot.error.no_subcommand": "Esse comando precisa de um subcomando. Veja a help deste comando para uma lista de subcomandos.",
    "bot.error.jpeg": "Sério? Um JPEG? que nojo! Por favor, crie um modelo PNG.",
    "bot.error.no_private_message": "Esse comando só funciona na guild.",
    "bot.error.unhandled_command_error": "Ocorreu um erro com esse comando. O desenvolvedor foi notificado.",

    # Command brief help
    "brief.alertchannel": "Definir ou desabilitar o canal usado para alertas de atualização.",
    "brief.alertchannel.clear": "Desabilita o canal de alerta.",
    "brief.alertchannel.set": "Define o canal de alerta.",
    "brief.autoscan": "Alterna automaticamente visualização e diferença.",
    "brief.canvas": "Define o site padrão do canvas para essa guild.",
    "brief.canvas.pixelcanvas": "Define o canvas padrão para o Pixelcanvas.io.",
    "brief.canvas.pixelzio": "Define o canvas padrão para o Pixelz.io.",
    "brief.canvas.pixelzone": "Define o canvas padrão para o Pixelzone.io.",
    "brief.canvas.pxlsspace": "Define o canvas padrão para o to Pxls.space.",
    "brief.changelog": "Obtém um link para minha página de lançamentos.",
    "brief.diff": "Verifica o status de conclusão de um template no canvas.",
    "brief.diff.pixelcanvas": "Cria um diff usando o Pixelcanvas.io.",
    "brief.diff.pixelzio": "Cria um diff usando Pixelz.io.",
    "brief.diff.pixelzone": "Cria um diff usando Pixelzone.io.",
    "brief.diff.pxlsspace": "Cria um diff usando Pxls.space",
    "brief.ditherchart": "Obtém um gráfico de cores do canvas combinando varias delas.",
    "brief.ditherchart.pixelcanvas": "Obtém um gráfico de combinação de cores do Pixelcanvas.io.",
    "brief.ditherchart.pixelzio": "Obtém um gráfico de combinação de cores do Pixelz.io.",
    "brief.ditherchart.pixelzone": "Obtém um gráfico de combinação de cores do Pixelzone.io.",
    "brief.ditherchart.pxlsspace": "Obtém um gráfico de combinação de cores do Pxls.space.",
    "brief.github": "Obtém um link para o meu repositório no GitHub.",
    "brief.gridify": "Adiciona grade a um template.",
    "brief.help": "Exibe esta mensagem.",
    "brief.invite": "Obtém meu link de convite.",
    "brief.language": "Define meu idioma.",
    "brief.listemotes": "Lista todos os emoji animados que eu conheço.",
    "brief.ping": "Pong!",
    "brief.prefix": "Define meu prefixo de comando para essa guild.",
    "brief.preview": "Visualiza o canvas em uma determinada coordenada.",
    "brief.preview.pixelcanvas": "Cria uma visualização usando o Pixelcanvas.io.",
    "brief.preview.pixelzio": "Cria uma visualização usando o Pixelz.io.",
    "brief.preview.pixelzone": "Cria uma visualização usando o Pixelzone.io.",
    "brief.preview.pxlsspace": "Cria uma visualização usando o Pxls.space.",
    "brief.quantize": "Rusticamente converte uma imagem para a paleta de uma canvas.",
    "brief.quantize.pixelcanvas": "Converte cores usando a paleta do Pixelcanvas.io.",
    "brief.quantize.pixelzio": "Converte cores usando a paleta do Pixelz.io.",
    "brief.quantize.pixelzone": "Converte cores usando a paleta do Pixelzone.io.",
    "brief.quantize.pxlsspace": "Converte cores usando a paleta do Pxls.space.",
    "brief.register": "Alterna a substituição de emojis animados para um usuário.",
    "brief.registerguild": "Alterna o compartilhamento de emojis para essa guild.",
    "brief.repeat": "Repete o último comando do canvas usado.",
    "brief.suggest": "Envia uma sugestão para o desenvolvedor.",
    "brief.version": "Obtém o número de minha versão.",

    # Command long help
    "help.alertchannel": """Se um canal de alerta estiver configurado, postarei uma mensagem nesse canal sempre que o número da minha versão for alterado para alertar você sobre as atualizações.""",
    "help.alertchannel.clear": """Isso efetivamente desabilita os alertas de atualização até que um novo canal seja definido.""",
    "help.alertchannel.set":
        """Use a sintaxe #channel com este comando para garantir que o canal correto esteja configurado.
    
        Este comando só pode ser usado por membros com a permissão de administrador.""",
    "help.autoscan":
        """Se habilitado, vou ver todas as mensagens por coordenadas e automaticamente criar previews e diffs de acordo com estas regras:
        - Qualquer mensagem com coordenadas no formato "@ 0, 0" acionará uma visualização para o canvas padrão.
        - Qualquer mensagem com um link para um canvas suportado acionará uma visualização para essa tela.
        - Qualquer mensagem com coordenadas no formato "0,0" com um PNG anexado acionará um diff para o canvas padrão.
        - As visualizações têm precedência sobre os diffs
        
        Veja 'setdefaultcanvas' para mais informações sobre o canvas padrão.
        
        Somente usuários com a função Administrador podem usar este comando.""",
    "help.canvas":
        """O canvas padrão é o canvas que será usado para visualizações automáticas ou diferenças acionadas pelo rastreamento automático. (Veja 'autoscan')

        Padrão para Pixelcanvas.io.

        Este comando só pode ser usado por membros com a permissão de Administrador.""",
    "help.canvas.pixelcanvas": """Este comando só pode ser usado por membros com a permissão de Administrador.""",
    "help.canvas.pixelzio": """Este comando só pode ser usado por membros com a permissão de Administrador.""",
    "help.canvas.pixelzone": """Este comando só pode ser usado por membros com a permissão de Administrador.""",
    "help.canvas.pxlsspace": """Este comando só pode ser usado por membros com a permissão de Administrador.""",
    "help.changelog": None,
    "help.diff":
        """Pega um template enviado, e compara ao estado atual do canvas e calcula a sua conclusão. Também irá gerar uma imagem mostrando onde estão os pixels inacabados.
        
        Se o modelo for menor que 200x200, você poderá criar uma imagem maior com um fator de zoom. (exemplo: "0,0 # 4) Você não pode ampliar uma imagem para ser maior que 400x400.
        
        O template deve estar no formato PNG.
        
        NOTA: Pixels "cores erradas" são pixels que não fazem parte da paleta do canvas. (Veja `quantize`)
        
        Se o autoscan estiver ativado, isso acontece automaticamente usando o canvas padrão. (Veja 'autoscan' e 'setdefaultcanvas')""",
    "help.diff.pixelcanvas": None,
    "help.diff.pixelzio": None,
    "help.diff.pixelzone": None,
    "help.diff.pxlsspace": None,
    "help.ditherchart": None,
    "help.ditherchart.pixelcanvas": None,
    "help.ditherchart.pixelzio": None,
    "help.ditherchart.pixelzone": None,
    "help.ditherchart.pxlsspace": None,
    "help.github": None,
    "help.gridify":
        """Pega um template anexada e cria um versão em grade para uma referência mais fácil. Use o parâmetro 'size' para definir o tamanho dos pixels individuais. (Padrão 1) Você não pode ampliar uma imagem para ser maior que 1000x1000.""",
    "help.help": None,
    "help.invite": None,
    "help.language": """Use this command with no arguments to see the current and available languages.""",
    "help.listemotes": """Veja 'registerserver' para mais informações sobre o compartilhamento de emojis.""",
    "help.ping": None,
    "help.prefix":
        """Comprimento máximo é de 5 caracteres. Você realmente não deveria precisar de mais de 2.

        Este comando só pode ser usado por membros com a permissão de Administrador.""",
    "help.preview":
        """Dado uma coordenada ou uma URL, rende uma visualização ao vivo do canvas nessas coordenadas.
        
        Você pode criar uma visualização ampliada adicionando um fator de zoom. (Exemplo, "0, 0 # 4") O zoom máximo é 16.
        
        Se o autoscan estiver ativado, isso acontece automaticamente usando o canvas padrão. (Veja 'autoscan' e 'setdefaultcanvas')""",
    "help.preview.pixelcanvas": None,
    "help.preview.pixelzio": None,
    "help.preview.pixelzone": None,
    "help.preview.pxlsspace": None,
    "help.quantize":
        """Pega uma imagem anexada e converte suas cores na paleta de um determinado canvas.
        
        Isso deve ser usado principalmente se o comando 'pcdiff' estiver informando que seu modelo tem 'cores erradas. Usar esse comando para criar modelos a partir de imagens brutas não é sugerido.""",
    "help.quantize.pixelcanvas": None,
    "help.quantize.pixelzio": None,
    "help.quantize.pixelzone": None,
    "help.quantize.pxlsspace": None,
    "help.register":
        """Se você optou por ativar este comando, eu assistirei a qualquer momento que você tentar usar um emoji animado e substituir sua mensagem por outra que tenha o emoji nela. Você só precisa se inscrever uma vez para que isso se aplique a todas as guilds. Use este comando novamente para desativar.
        
        Se a sua guild tiver optado pelo compartilhamento de emojis, você poderá usar emojis de qualquer outra guild que também o tenha habilitado. (Veja 'registerguild')
        
        Eu não posso usar emojis animados das guilds que eu não estou, então eu não posso usar emoji animados de outras guilds postadas por usuários do Discord Nitro ou de guilds integradas ao Twitch.
        
        Esse recurso requer que eu tenha a permissão Gerenciar Mensagens.""",
    "help.registerguild":
        """Se ativado, os membros dessa guild poderão usar emojis animados de qualquer outra guild que também tenha optado por participar. Em troca, emojis animados desta guild também podem ser usados por qualquer uma dessas guilds. Isso não é necessário para usar emoticons animados desta guild.
        
        NOTA: Optar pelo compartilhamento de emojis permitirá que outras guildas vejam o nome e o ID dessa guild. Se sua guild não é uma guild pública, habilitar esse recurso não é recomendado.
        
        Esse comando só pode ser usado por membros com a permissão Gerenciar Emojis.""",
    "help.repeat": "Este comando aplica-se apenas a 'preview', 'diff' e suas invocações automáticas. Apenas 50 mensagens de retorno serão pesquisadas.",
    "help.suggest": None,
    "help.version": None,

    # Command names
    "command.alertchannel": "alertchannel",
    "command.alertchannel.clear": "clear",
    "command.alertchannel.set": "set",
    "command.autoscan": "autoscan",
    "command.canvas": "canvas",
    "command.canvas.pixelcanvas": "pixelcanvas",
    "command.canvas.pixelzio": "pixelzio",
    "command.canvas.pixelzone": "pixelzone",
    "command.canvas.pxlsspace": "pxlsspace",
    "command.changelog": "changelog",
    "command.diff": "diff",
    "command.diff.pixelcanvas": "pixelcanvas",
    "command.diff.pixelzio": "pixelzio",
    "command.diff.pixelzone": "pixelzone",
    "command.diff.pxlsspace": "pxlsspace",
    "command.ditherchart": "ditherchart",
    "command.ditherchart.pixelcanvas": "pixelcanvas",
    "command.ditherchart.pixelzio": "pixelzio",
    "command.ditherchart.pixelzone": "pixelzone",
    "command.ditherchart.pxlsspace": "pxlsspace",
    "command.github": "github",
    "command.gridify": "gridify",
    "command.help": "help",
    "command.invite": "invite",
    "command.language": "language",
    "command.listemotes": "listemotes",
    "command.ping": "ping",
    "command.prefix": "prefix",
    "command.preview": "preview",
    "command.preview.pixelcanvas": "pixelcanvas",
    "command.preview.pixelzio": "pixelzio",
    "command.preview.pixelzone": "pixelzone",
    "command.preview.pxlsspace": "pxlsspace",
    "command.quantize": "quantize",
    "command.quantize.pixelcanvas": "pixelcanvas",
    "command.quantize.pixelzio": "pixelzio",
    "command.quantize.pixelzone": "pixelzone",
    "command.quantize.pxlsspace": "pxlsspace",
    "command.register": "register",
    "command.registerguild": "registerguild",
    "command.repeat": "repeat",
    "command.suggest": "suggest",
    "command.version": "version",

    # Command signatures
    "signature.alertchannel": "alertchannel <subcomando>",
    "signature.alertchannel.clear": "alertchannel clear",
    "signature.alertchannel.set": "alertchannel set <canal>",
    "signature.autoscan": "autoscan",
    "signature.canvas": "canvas <canvas>",
    "signature.canvas.pixelcanvas": "canvas pixelcanvas",
    "signature.canvas.pixelzio": "canvas pixelzio",
    "signature.canvas.pixelzone": "canvas pixelzone",
    "signature.canvas.pxlsspace": "canvas pxlsspace",
    "signature.changelog": "changelog",
    "signature.diff": "diff <subcomando>",
    "signature.diff.pixelcanvas": "diff pixelcanvas <coordenadas> (zoom)",
    "signature.diff.pixelzio": "diff pixelzio <coordenadas> (zoom)",
    "signature.diff.pixelzone": "diff pixelzone <coordenadas> (zoom)",
    "signature.diff.pxlsspace": "diff pxlsspace <coordenadas> (zoom)",
    "signature.ditherchart": "ditherchart <subcomando>",
    "signature.ditherchart.pixelcanvas": "ditherchart pixelcanvas",
    "signature.ditherchart.pixelzio": "ditherchart pixelzio",
    "signature.ditherchart.pixelzone": "ditherchart pixelzone",
    "signature.ditherchart.pxlsspace": "ditherchart pxlsspace",
    "signature.github": "github",
    "signature.gridify": "gridify (tamanho)",
    "signature.help": "help",
    "signature.invite": "invite",
    "signature.language": "language (código)",
    "signature.listemotes": "listemotes",
    "signature.ping": "ping",
    "signature.prefix": "prefix <prefixo>",
    "signature.preview": "preview <subcommand>",
    "signature.preview.pixelcanvas": "preview pixelcanvas <coordenadas> (zoom)",
    "signature.preview.pixelzio": "preview pixelzio <coordenadas> (zoom)",
    "signature.preview.pixelzone": "preview pixelzone <coordenadas> (zoom)",
    "signature.preview.pxlsspace": "preview pxlsspace <coordenadas> (zoom)",
    "signature.quantize": "quantize <subcomando>",
    "signature.quantize.pixelcanvas": "quantize pixelcanvas",
    "signature.quantize.pixelzio": "quantize pixelzio",
    "signature.quantize.pixelzone": "quantize pixelzone",
    "signature.quantize.pxlsspace": "quantize pxlsspace",
    "signature.register": "register",
    "signature.registerguild": "registerguild",
    "signature.repeat": "repeat",
    "signature.suggest": "suggest <sugestão>",
    "signature.version": "version",
}
