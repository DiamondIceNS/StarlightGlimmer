STRINGS = {
    # General messages
    "bot.alert_update": "Eu atualizei para a versão **{0}**! Confira a página de ajuda de comandos para os novos comandos digite `{1}help`, ou visite https://github.com/DiamondIceNS/StarlightGlimmer/releases para o changelog completo.",
    "bot.description":
        """Oi! Eu sou a {0}! Estou aqui para ajudar a coordenar pixel art em sites de colocação de pixels.
        Eu tenho recursos como visualização de tela e verificação de templates que certamente serão úteis.
        Vamos começar a pintar pixels!""",
    "bot.discord_urls_only": "Eu só posso aceitar anexos de URLs do Discord.",
    "bot.help_ending_note": "Digite '{0}{1} <command>' para mais informações do comando.",
    "bot.ping": "Pinging...",
    "bot.pong": "Pong! | **{0}ms**",
    "bot.suggest": "Sua sugestão foi enviada. Obrigado por sua contribuição!",
    "bot.version": "O numero da minha versão é **{0}**",
    "bot.why": "Mas... por que?",
    "bot.yes_no": "\n  `0` - Não\n  `1` - Sim",
    "bot.yes_no_invalid": "Essa não é uma opção válida. Por favor, tente novamente.",
    "bot.yes_no_timed_out": "excedido o tempo.",

    # Animotes messages
    "animotes.guild_opt_in": "O compartilhamento de emojis foi **ativado** para essa guild.",
    "animotes.guild_opt_out": "O compartilhamento de emojis foi **desativado** para esta guild.",
    "animotes.member_opt_in": "Você optou com sucesso em **aceitar** a conversão de emojis.",
    "animotes.member_opt_out": "Você cancelou ** com êxito ** a conversão de emojis.",

    # Canvas messages
    "canvas.invalid_input": "Entrada inválida: não corresponde a nenhum nome de template ou formato de coordenadas suportadas.",
    "canvas.repeat_not_found": "Não foi possível encontrar um comando válido para repetir.",

    # Render messages
    "render.diff": "{0}/{1} | {2} erros | {3:.2f}% completo",
    "render.diff_bad_color": "{0}/{1} | {2} erros | {3} cores erradas | {4:.2f}% completo",
    "render.large_template": "(Processando template grande, isso pode levar alguns segundos ...)",
    "render.quantize": "Convertidos {0} pixels.",

    # Template messages
    "template.added": "Template '{0}' adicionado!",
    "template.duplicate_list_open": "Os seguintes templates já correspondem a esta imagem:\n```xl\n",
    "template.duplicate_list_close": "```\nCriar um novo template mesmo assim?",
    "template.info_added_by": "Adicionado por",
    "template.info_date_added": "Data adicionada",
    "template.info_date_modified": "Data aodificada",
    "template.info_canvas": "Canvas",
    "template.info_coords": "Coordenadas",
    "template.info_name": "Nome",
    "template.info_size": "Tamanho",
    "template.list_close": "\n// Use '{0}templates <pagina>' para ver essa página\n// Use '{0}templates info <nome>' para ver mais informações do template```",
    "template.list_no_templates": "Esta guild atualmente não possui templates.",
    "template.list_open": "**Lista de templates** - Pagina {0}/{1}\n```xl\n",
    "template.max_templates": "Esta guild já tem o número máximo de templates. Por favor, remova um template antes de adicionar outro.",
    "template.name_exists_ask_replace": "Um modelo com o nome '{0}' já existe para {1} em ({2}, {3}). Substituo?",
    "template.name_exists_no_permission": "Um template com esse nome já existe. Por favor escolha um nome diferente.",
    "template.name_not_found": "Não foi possível encontrar o template com nome `{0}`.",
    "template.name_too_long": "Esse nome é muito longo. Por favor use um nome a baixo de {0} caracteres.",
    "template.no_template_named": "Não há nenhum template chamado '{0}'.",
    "template.not_owner": "Você não tem permissão para modificar esse template.",
    "template.not_quantized": "Esta imagem contém cores que não fazem parte da paleta deste canvas. Você gostaria de converter?",
    "template.remove": "Removido com sucesso '{0}'.",
    "template.updated": "Template '{0}' atualizada!",

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
    "configuration.role_list": "**Lista de cargos**\n```xl\n"
                               "'botadmin'      - Pode fazer qualquer coisa que um administrador pode fazer\n"
                               "'templateadder' - Pode adicionar templates e remover templates que eles mesmos adicionaram\n"
                               "'templateadmin' - Pode adicionar e remover qualquer template\n"
                               "\n// Use '{0}cargo <digite>' para ver o cargo atual vinculado.\n```",
    "configuration.role_not_found": "Esse cargo não pôde ser encontrado.",
    "configuration.role_bot_admin_check": "Os privilégios de Bot admin estão atualmente atribuídos a `@{0}`.",
    "configuration.role_bot_admin_cleared": "Privilégios do Bot admin retirados com sucesso.",
    "configuration.role_bot_admin_not_set": "Os privilégios do  Bot admin não foram atribuídos a um cargo.",
    "configuration.role_bot_admin_set": "Privilégios de Bot admin atribuídos ao cargo `@{0}`.",
    "configuration.role_template_adder_check": "Os privilégios do Template adder estão atribuídos atualmente a `@{0}`.",
    "configuration.role_template_adder_cleared": "Privilégios do Template adder retirados com sucesso.",
    "configuration.role_template_adder_not_set": "Os privilégios do Template adder não foram atribuídos a um cargo.",
    "configuration.role_template_adder_set": "Privilégios do Template adder atribuídos ao cargo `@{0}`.",
    "configuration.role_template_admin_check": "Os privilégios do Template admin estão atualmente atribuídos a `@{0}`.",
    "configuration.role_template_admin_cleared": "Template admin privilégios retirados com sucesso.",
    "configuration.role_template_admin_not_set": "Template admin privilégios não foram atribuídos a um cargo.",
    "configuration.role_template_admin_set": "Template admin privilégios atribuídos ao cargo `@{0}`.",

    # Error messages
    "bot.error.bad_png": "Esta imagem parece estar corrompida. Tente salvá-la novamente com um editor de imagens ou usando `{0}{1}`.",
    "bot.error.command_on_cooldown": "Esse comando está em cooldown. Tente novamente em {0:.01f}s.",
    "bot.error.http_payload_error": "{0} parece estar tendo problemas de conexão. Tente mais tarde.",
    "bot.error.jpeg": "Sério? Um JPEG? que nojo! Por favor, crie um modelo PNG.",
    "bot.error.missing_attachment": "Esse comando requer um anexo.",
    "bot.error.no_canvas": "Esse comando requer um subcomando.",
    "bot.error.no_permission": "Você não tem permissão para usar esse comando.",
    "bot.error.no_png": "Esse comando requer uma imagem PNG.",
    "bot.error.no_subcommand": "Esse comando precisa de um subcomando. Veja a help deste comando para uma lista de subcomandos.",
    "bot.error.no_private_message": "Esse comando só funciona na guild.",
    "bot.error.pil_image_open_exception": "Ocorreu um erro ao tentar abrir uma imagem. Assegure-se de que a imagem fornecida não esteja corrompida.",
    "bot.error.template.http_error": "Não foi possível acessar o URL do template. (O anexo original foi excluído?)",
    "bot.error.unhandled_command_error": "Ocorreu um erro com esse comando. O desenvolvedor foi notificado.",
    "bot.error.url_error": "Esse URL é inválido. Eu só posso aceitar URLs de anexos do Discord.",

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
    "brief.register": "Optou em aderir substituição de emoji animado.",
    "brief.registerguild": "Optou em aderir compartilhar emojis para essa guild.",
    "brief.repeat": "Repete o último comando do canvas usado.",
    "brief.role": "Atribuir privilégios do bot a uma cargo.",
    "brief.role.botadmin": "Configurar privilégios do Bot Admin.",
    "brief.role.botadmin.clear": "Retire o cargo atribuído a Bot Admin",
    "brief.role.botadmin.set": "Defina o cargo atribuído ao Bot Admin",
    "brief.role.templateadder": "Configurar privilégios do Template Adder.",
    "brief.role.templateadder.clear": "Retire o cargo atribuído ao Template Adder.",
    "brief.role.templateadder.set": "Defina o cargo atribuído ao Template Adder.",
    "brief.role.templateadmin": "Configurar privilégios do Template admin.",
    "brief.role.templateadmin.clear": "Retire a função atribuída ao Template Admin.",
    "brief.role.templateadmin.set": "Defina o cargo atribuído ao Template Admin.",
    "brief.suggest": "Envia uma sugestão para o desenvolvedor.",
    "brief.template": "Gerencia templates.",
    "brief.template.add": "Adiciona um template.",
    "brief.template.add.pixelcanvas": "Adiciona um template para Pixelcanvas.io.",
    "brief.template.add.pixelzio": "Adiciona um template para Pixelz.io.",
    "brief.template.add.pixelzone": "Adiciona um template para Pixelzone.io.",
    "brief.template.add.pxlsspace": "Adiciona um template para Pxls.space.",
    "brief.template.info": "Exibe informações sobre um template.",
    "brief.template.remove": "Remove um template.",
    "brief.unregister": "Desativada a substituição de emoji animado.",
    "brief.unregisterguild": "Desativado o compartilhamento de emojis para essa guild.",
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
        """Pega um template ou um anexo de imagem, compara-o ao estado atual do canvas e calcula a sua conclusão. Também irá gerar uma imagem mostrando onde estão os pixels restando.
        
        Se a imagem for menor que 200x200, você poderá criar uma imagem maior com um fator de zoom. (ou seja, "0, 0 # 4) Você não pode ampliar uma imagem para ser maior que 400x400.
        
        Os anexos devem ser em formato PNG.
        
        NOTA: "cores erradas" são pixels que não fazem parte da paleta do canvas. (Veja `quantize`) para converter.
        
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
    "help.gridify": "Obtém um template ou um anexo de imagem e cria uma versão em grade para uma referência mais fácil. Use o parâmetro 'size' para definir o tamanho dos pixels individuais. (Padrão 1) Você não pode ampliar uma imagem para conter mais de 4 milhões de pixels.",
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
        
        Você pode criar uma visualização ampliada adicionando um fator de zoom. (Exemplo, "0, 0 # 4") O zoom máximo é 16. Você também pode criar uma visualização com menos zoom usando um zoom negativo. (isto é, "0,0 # -4") O zoom mínimo é de -8.
        
        Se o autoscan estiver ativado, isso acontece automaticamente usando o canvas padrão. (Veja 'autoscan' e 'setdefaultcanvas')""",
    "help.preview.pixelcanvas": None,
    "help.preview.pixelzio": None,
    "help.preview.pixelzone": None,
    "help.preview.pxlsspace": None,
    "help.quantize":
        """Pega um template ou um anexo de imagem e converte suas cores na paleta de uma determinada canvas.
        
        Isso deve ser usado principalmente se o comando 'pcdiff' estiver informando que sua imagem tem 'cores erradas'. Usar esse comando para criar modelos a partir de uma imagem bruta não é sugerido.""",
    "help.quantize.pixelcanvas": None,
    "help.quantize.pixelzio": None,
    "help.quantize.pixelzone": None,
    "help.quantize.pxlsspace": None,
    "help.register":
        """Se você optou por ativar este comando, eu assistirei a qualquer momento que você tentar usar um emoji animado e substituir sua mensagem por outra que tenha o emoji nela. Você só precisa se inscrever uma vez para que isso se aplique a todas as guilds. Use 'unregister' para desativar.
        
        Se a sua guild tiver optado pelo compartilhamento de emojis, você poderá usar emojis de qualquer outra guild que também o tenha habilitado. (Veja 'registerguild')
        
        Eu não posso usar emojis animados das guilds que eu não estou, então eu não posso usar emoji animados de outras guilds postadas por usuários do Discord Nitro ou de guilds integradas ao Twitch.
        
        Esse recurso requer que eu tenha a permissão Gerenciar Mensagens.""",
    "help.registerguild":
        """Se ativado, os membros dessa guild poderão usar emojis animados de qualquer outra guild que também tenha optado por participar. Em troca, emojis animados desta guild também podem ser usados por qualquer uma dessas guilds. Isso não é necessário para usar emoticons animados desta guild. Use 'unregisterguild' para desativar.
        
        NOTA: Optar pelo compartilhamento de emojis permitirá que outras guildas vejam o nome e o ID dessa guild. Se sua guild não é uma guild pública, habilitar esse recurso não é recomendado.
        
        Esse comando só pode ser usado por membros com a permissão Gerenciar Emojis.""",
    "help.repeat": "Este comando aplica-se apenas a 'preview', 'diff' e suas invocações automáticas. Apenas 50 mensagens de retorno serão pesquisadas.",
    "help.role":
        """Os administradores podem usar esse comando para criar cargos em suas guilds que concedem privilégios especiais aos usuários ao usar meus comandos.
    
        Use este comando sem argumentos para ver quais configurações de privilégio estão disponíveis.
    
        Consulte a página de ajuda de qualquer um dos subcomandos a seguir para obter mais informações sobre o que cada privilégio concede.
        """,
    "help.role.botadmin": "Se um usuário tiver um cargo com esse privilégio vinculado a ele, esse usuário poderá usar qualquer comando sem restrições. Eles terão as mesmas permissões que os Administradores da guild.",
    "help.role.templateadder":
    """Se um usuário tiver um cargo com esse privilégio vinculado a ele, esse usuário poderá adicionar templates usando o comando 'templates'. Eles também podem remover templates, mas somente se esse usuário foi quem originalmente o adicionou.
    
        NOTA: Se este privilégio estiver definido para qualquer cargo, todos os outros membros perderão a capacidade de adicionar templates. Se você quiser permitir que qualquer usuário adicione templates, não defina isso.""",
    "help.role.templateadmin": "Se um usuário tiver um cargo com esse privilégio vinculado a ele, esse usuário poderá adicionar e remover qualquer modelo usando o comando 'templates', independentemente de ser dono. Isso é útil se você quiser conceder aos membros controle total sobre os templates, mas nem todas as funções do bot.",
    "help.suggest": None,
    "help.template": "Use este comando sem argumentos para visualizar uma lista de todos os templates adicionados.",
    "help.template.add":
        """Esse comando pode aceitar um anexo de arquivo direto ou uma URL de anexo do Discord. O modelo deve estar no formato PNG e já deve estar convertido para a paleta do canvas à qual pertence. Se a imagem não for convertida, o comando ira oferecer para converter para você. Uma guild pode ter até 25 templates a qualquer momento.
        
        Apenas um template pode ser adicionado com qualquer nome (máximo de 32 caracteres). Se você adicionar um segundo template com o mesmo nome, ele substituirá o primeiro modelo. Você só pode sobrescrever seus próprios templates, a menos que seja um Template Admin, Bot Admin ou tenha a permissão de Administrador (consulte 'role').
        
        Por padrão, todos podem usar este comando. Se o Template Adder privilégio estiver vinculado a qualquer cargo, somente usuários que são Template Adders e acima podem usar este comando (consulte 'role').
        
        Um template é armazenado como um URL de um anexo. Se a mensagem que carregou esse anexo for excluída, o template de referencia sera quebrado. Recomenda-se que você salve cópias de backup de templates no seu computador apenas por precaução.""",
    "help.template.remove": "Este comando só pode ser usado se o template que está sendo removido tiver sido adicionado por você, a menos que você seja um Template Admin, Bot Admin ou tenha a permissão de Administrador (consulte 'role').",
    "help.template.add.pixelcanvas": None,
    "help.unregister": "Veja 'register'.",
    "help.unregisterguild":
        """Veja 'registerguild'.
        
        Esse comando só pode ser usado por membros com a permissão Gerenciar Emojis.""",
    "help.version": None,

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
    "signature.role": "role (cargo)",
    "signature.role.botadmin": "role botadmin (set|clear)",
    "signature.role.botadmin.clear": "role botadmin clear",
    "signature.role.botadmin.set": "role botadmin set <@cargo nome>",
    "signature.role.templateadder": "role templateadder (set|clear)",
    "signature.role.templateadder.clear": "role templateadder clear",
    "signature.role.templateadder.set": "role templateadder set <@cargo nome>",
    "signature.role.templateadmin": "role templateadmin (set|clear)",
    "signature.role.templateadmin.clear": "role templateadmin clear",
    "signature.role.templateadmin.set": "role templateadmin set <@cargo nome>",
    "signature.suggest": "suggest <sugestão>",
    "signature.template": "[template|t] (subcomando)",
    "signature.template.add": "[template|t] add (canvas) <nome> <x> <y> (url)",
    "signature.template.add.pixelcanvas": "[template|t] add [pixelcanvas|pc] <nome> <x> <y> (url)",
    "signature.template.add.pixelzio": "[template|t] add [pixelzio|pzi] <nome> <x> <y> (url)",
    "signature.template.add.pixelzone": "[template|t] add [pixelzone|pz] <nome> <x> <y> (url)",
    "signature.template.add.pxlsspace": "[template|t] add [pxlsspace|ps] <nome> <x> <y> (url)",
    "signature.template.info": "[template|t] info",
    "signature.template.remove": "[template|t] remove",
    "signature.unregister": "unregister",
    "signature.unregisterguild": "unregisterguild",
    "signature.version": "version",
}
