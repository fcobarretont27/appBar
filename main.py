import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp

# NÃO definir Window.size fixo - deixa o sistema gerenciar
# Apenas define a cor de fundo
Window.clearcolor = get_color_from_hex('#121212')

# Cores do tema escuro
BG_DARK = get_color_from_hex('#121212')
BG_CARD = get_color_from_hex('#1E1E1E')
BG_INPUT = get_color_from_hex('#2C2C2C')
PRIMARY_COLOR = get_color_from_hex('#3498DB')
SUCCESS_COLOR = get_color_from_hex('#27AE60')
DANGER_COLOR = get_color_from_hex('#E74C3C')
TEXT_PRIMARY = get_color_from_hex('#FFFFFF')
TEXT_SECONDARY = get_color_from_hex('#B0B0B0')

# Dados de garrafas
garrafas = {}
ARQUIVO = "garrafas.json"


def load_garrafas():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                data = json.load(f)
                for nome, dados in data.items():
                    garrafas[nome] = tuple(dados)
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")


def save_garrafas():
    try:
        data = {nome: list(dados) for nome, dados in garrafas.items()}
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Erro ao salvar:", e)


class SimpleTextInput(TextInput):
    """TextInput simplificado com cores"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = BG_INPUT
        self.foreground_color = TEXT_PRIMARY
        self.cursor_color = PRIMARY_COLOR
        self.hint_text_color = TEXT_SECONDARY
        self.padding = [dp(12), dp(12), dp(12), dp(12)]
        self.size_hint_y = None
        self.height = dp(50)
        self.font_size = sp(16)
        self.border = (0, 0, 0, 0)


class GarrafaItem(BoxLayout):
    """Item da lista de garrafas"""
    def __init__(self, nome, volume, **kwargs):
        super().__init__(**kwargs)
        self.nome = nome
        self.orientation = 'horizontal'
        self.spacing = dp(8)
        self.size_hint_y = None
        self.height = dp(55)
        self.padding = [dp(12), dp(8), dp(8), dp(8)]

        self.bind(pos=self.update_rect, size=self.update_rect)

        lbl_nome = Label(
            text=nome,
            font_size=sp(15),
            color=TEXT_PRIMARY,
            halign='left',
            valign='middle',
            size_hint_x=0.6,
            bold=True
        )
        lbl_nome.bind(texture_size=lbl_nome.setter('size'))

        lbl_vol = Label(
            text=f"{volume:.0f} mL",
            font_size=sp(13),
            color=TEXT_SECONDARY,
            halign='center',
            valign='middle',
            size_hint_x=0.25
        )
        lbl_vol.bind(texture_size=lbl_vol.setter('size'))

        btn_sel = Button(
            text=">",
            font_size=sp(18),
            color=TEXT_PRIMARY,
            background_color=PRIMARY_COLOR,
            size_hint_x=0.15,
            height=dp(35),
            size_hint_y=None
        )
        btn_sel.bind(on_press=self.selecionar)

        self.add_widget(lbl_nome)
        self.add_widget(lbl_vol)
        self.add_widget(btn_sel)

    def update_rect(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BG_CARD)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

    def selecionar(self, instance):
        if hasattr(self, 'on_select'):
            self.on_select(self.nome)


class CardResultado(BoxLayout):
    """Card para exibir resultados"""
    def __init__(self, titulo, valor, cor, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = [dp(10), dp(8)]
        self.spacing = dp(4)

        self.bind(pos=self.update_rect, size=self.update_rect)

        lbl_titulo = Label(
            text=titulo,
            font_size=sp(11),
            color=TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(20),
            halign='center'
        )
        lbl_titulo.bind(texture_size=lbl_titulo.setter('size'))

        self.lbl_valor = Label(
            text=valor,
            font_size=sp(18),
            color=cor,
            size_hint_y=None,
            height=dp(35),
            halign='center',
            bold=True
        )
        self.lbl_valor.bind(texture_size=self.lbl_valor.setter('size'))

        self.add_widget(lbl_titulo)
        self.add_widget(self.lbl_valor)

    def update_rect(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BG_CARD)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )

    def atualizar_valor(self, novo_valor):
        self.lbl_valor.text = novo_valor


class BottomNavButton(Button):
    """Botão da navbar com apenas ícone (asset) usando caracteres Unicode"""
    def __init__(self, icon, **kwargs):
        super().__init__(text=icon, **kwargs)
        self.font_size = sp(28)
        self.color = TEXT_SECONDARY
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.background_down = ''
        self.size_hint = (1, 1)
        self.is_active = False

    def activate(self):
        self.is_active = True
        self.color = PRIMARY_COLOR

    def deactivate(self):
        self.is_active = False
        self.color = TEXT_SECONDARY


class BottomNavBar(BoxLayout):
    """Bottom Navigation Bar apenas com ícones"""
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.size_hint_y = None
        self.height = dp(60)
        self.orientation = 'vertical'

        with self.canvas.before:
            Color(*BG_CARD)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        grid = GridLayout(cols=3, rows=1, spacing=0, size_hint=(1, 1))
        self.buttons = {}

        # Ícones: gráfico, mais, lixeira
        btn_calculo = BottomNavButton("📊")
        btn_calculo.bind(on_release=lambda x: self.switch_screen('calculo'))
        self.buttons['calculo'] = btn_calculo
        grid.add_widget(btn_calculo)

        btn_cadastro = BottomNavButton("➕")
        btn_cadastro.bind(on_release=lambda x: self.switch_screen('cadastro'))
        self.buttons['cadastro'] = btn_cadastro
        grid.add_widget(btn_cadastro)

        btn_exclusao = BottomNavButton("🗑️")
        btn_exclusao.bind(on_release=lambda x: self.switch_screen('exclusao'))
        self.buttons['exclusao'] = btn_exclusao
        grid.add_widget(btn_exclusao)

        self.add_widget(grid)
        self.activate_button('calculo')

    def update_rect(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size

    def switch_screen(self, screen_name):
        self.screen_manager.current = screen_name
        self.activate_button(screen_name)

    def activate_button(self, active_screen):
        for name, button in self.buttons.items():
            if name == active_screen:
                button.activate()
            else:
                button.deactivate()


class CalculoScreen(Screen):
    """Tela de cálculo principal"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.build_ui()

    def build_ui(self):
        scroll = ScrollView()
        layout = BoxLayout(orientation="vertical", padding=[dp(15), dp(10), dp(15), dp(10)], spacing=dp(12), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Header
        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(70), spacing=dp(5))
        lbl_titulo = Label(
            text="CALCULADORA DE DOSES",
            font_size=sp(22),
            color=PRIMARY_COLOR,
            size_hint_y=None,
            height=dp(40),
            bold=True,
            halign='center'
        )
        lbl_titulo.bind(texture_size=lbl_titulo.setter('size'))

        lbl_sub = Label(
            text="Doses padrão: 50 mL",
            font_size=sp(12),
            color=TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(20),
            halign='center'
        )
        lbl_sub.bind(texture_size=lbl_sub.setter('size'))

        header.add_widget(lbl_titulo)
        header.add_widget(lbl_sub)
        layout.add_widget(header)

        # Busca
        layout.add_widget(Label(
            text="🔍 BUSCAR GARRAFA",
            font_size=sp(12),
            color=PRIMARY_COLOR,
            size_hint_y=None,
            height=dp(25),
            bold=True,
            halign='left'
        ))

        self.txt_busca = SimpleTextInput(
            hint_text="Digite o nome da garrafa...",
            multiline=False
        )
        self.txt_busca.bind(text=self.on_busca_text)
        layout.add_widget(self.txt_busca)

        # Lista de garrafas
        layout.add_widget(Label(
            text="📋 GARRAFAS DISPONÍVEIS",
            font_size=sp(12),
            color=PRIMARY_COLOR,
            size_hint_y=None,
            height=dp(25),
            bold=True,
            halign='left'
        ))

        lista_scroll = ScrollView(size_hint_y=None, height=dp(180))
        self.lista_layout = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.lista_layout.bind(minimum_height=self.lista_layout.setter('height'))
        lista_scroll.add_widget(self.lista_layout)
        layout.add_widget(lista_scroll)

        # Garrafa selecionada
        layout.add_widget(Label(
            text="🎯 GARRAFA SELECIONADA",
            font_size=sp(12),
            color=SUCCESS_COLOR,
            size_hint_y=None,
            height=dp(25),
            bold=True,
            halign='left'
        ))

        self.nome_garrafa = SimpleTextInput(
            readonly=True,
            hint_text="Nenhuma garrafa selecionada"
        )
        layout.add_widget(self.nome_garrafa)

        # Quantidade e peso
        grid_dados = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))

        box_qtd = BoxLayout(orientation='vertical', spacing=dp(5))
        box_qtd.add_widget(Label(
            text="📦 QUANTIDADE",
            font_size=sp(10),
            color=TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(20),
            halign='left'
        ))
        self.qtd = SimpleTextInput(text="1", multiline=False)
        box_qtd.add_widget(self.qtd)

        box_peso = BoxLayout(orientation='vertical', spacing=dp(5))
        box_peso.add_widget(Label(
            text="⚖️ PESO TOTAL (g)",
            font_size=sp(10),
            color=TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(20),
            halign='left'
        ))
        self.peso = SimpleTextInput(multiline=False, hint_text="Ex: 1250")
        box_peso.add_widget(self.peso)

        grid_dados.add_widget(box_qtd)
        grid_dados.add_widget(box_peso)
        layout.add_widget(grid_dados)

        # Botão calcular
        self.bt_calcular = Button(
            text="📊 CALCULAR DOSES",
            font_size=sp(18),
            color=TEXT_PRIMARY,
            background_color=PRIMARY_COLOR,
            size_hint_y=None,
            height=dp(55)
        )
        self.bt_calcular.bind(on_press=self.calcular)
        layout.add_widget(self.bt_calcular)

        # Resultados
        layout.add_widget(Label(
            text="📈 RESULTADOS",
            font_size=sp(12),
            color=SUCCESS_COLOR,
            size_hint_y=None,
            height=dp(25),
            bold=True,
            halign='left'
        ))

        grid_resultados = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(160))

        self.card_volume_total = CardResultado("Volume Total", "0.0 mL", SUCCESS_COLOR)
        grid_resultados.add_widget(self.card_volume_total)

        self.card_doses_total = CardResultado("Doses (50 mL)", "0.0 doses", SUCCESS_COLOR)
        grid_resultados.add_widget(self.card_doses_total)

        self.card_volume_por = CardResultado("Por Garrafa", "0.0 mL", PRIMARY_COLOR)
        grid_resultados.add_widget(self.card_volume_por)

        self.card_doses_por = CardResultado("Doses/Garrafa", "0.0 doses", PRIMARY_COLOR)
        grid_resultados.add_widget(self.card_doses_por)

        layout.add_widget(grid_resultados)
        layout.add_widget(Widget(size_hint_y=None, height=dp(10)))

        scroll.add_widget(layout)
        self.add_widget(scroll)
        self.atualizar_lista_garrafas()

    def atualizar_lista_garrafas(self):
        self.lista_layout.clear_widgets()
        filtro = self.txt_busca.text.lower() if hasattr(self, 'txt_busca') else ""

        if filtro == "":
            lista = list(garrafas.keys())
        else:
            lista = [n for n in garrafas.keys() if filtro in n.lower()]

        if not lista:
            msg = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60))
            msg.add_widget(Label(
                text="Nenhuma garrafa encontrada\nClique em '+' para cadastrar",
                font_size=sp(12),
                color=TEXT_SECONDARY,
                halign='center'
            ))
            self.lista_layout.add_widget(msg)
        else:
            for nome in lista:
                vol_total = garrafas[nome][2]
                item = GarrafaItem(nome, vol_total)
                item.on_select = self.selecionar_garrafa
                self.lista_layout.add_widget(item)

    def on_busca_text(self, instance, value):
        Clock.schedule_once(lambda dt: self.atualizar_lista_garrafas(), 0.05)

    def selecionar_garrafa(self, nome):
        self.nome_garrafa.text = nome
        self.nome_garrafa.background_color = get_color_from_hex('#3C3C3C')
        Clock.schedule_once(lambda dt: setattr(self.nome_garrafa, 'background_color', BG_INPUT), 0.5)

    def calcular(self, *args):
        if not self.nome_garrafa.text or self.nome_garrafa.text not in garrafas:
            self.app.mostrar_popup("Atenção", "Selecione uma garrafa válida.")
            return

        try:
            peso_atual = float(self.peso.text) if self.peso.text else 0
            qtd = float(self.qtd.text) if self.qtd.text else 1
            if qtd <= 0:
                raise ValueError
            if peso_atual <= 0:
                self.app.mostrar_popup("Atenção", "Informe o peso total.")
                return
        except ValueError:
            self.app.mostrar_popup("Erro", "Peso e quantidade devem ser números válidos.")
            return

        nome = self.nome_garrafa.text
        peso_vazio, peso_cheio, vol_total, densidade = garrafas[nome]

        massa_liquido_atual = peso_atual - (qtd * peso_vazio)
        if massa_liquido_atual < 0:
            self.app.mostrar_popup("Erro", "Peso total muito baixo para a quantidade de garrafas.")
            return

        volume_total = massa_liquido_atual / densidade
        doses_total = volume_total / 50.0
        volume_por_garrafa = volume_total / qtd
        doses_por_garrafa = volume_por_garrafa / 50.0

        self.card_volume_total.atualizar_valor(f"{volume_total:.1f} mL")
        self.card_doses_total.atualizar_valor(f"{doses_total:.1f} doses")
        self.card_volume_por.atualizar_valor(f"{volume_por_garrafa:.1f} mL")
        self.card_doses_por.atualizar_valor(f"{doses_por_garrafa:.1f} doses")


class CadastroScreen(Screen):
    """Tela de cadastro de garrafas"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.build_ui()

    def build_ui(self):
        scroll = ScrollView()
        layout = BoxLayout(orientation="vertical", padding=[dp(20), dp(15), dp(20), dp(15)], spacing=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        layout.add_widget(Label(
            text="➕ CADASTRAR GARRAFA",
            font_size=sp(20),
            color=SUCCESS_COLOR,
            size_hint_y=None,
            height=dp(50),
            bold=True,
            halign='center'
        ))

        layout.add_widget(Widget(size_hint_y=None, height=dp(20)))

        layout.add_widget(Label(text="Nome da garrafa:", font_size=sp(14), color=TEXT_PRIMARY, size_hint_y=None, height=dp(25)))
        self.nome = SimpleTextInput(hint_text="Ex: Garrafa 500mL", multiline=False)
        layout.add_widget(self.nome)

        layout.add_widget(Label(text="Peso vazio (g):", font_size=sp(14), color=TEXT_PRIMARY, size_hint_y=None, height=dp(25)))
        self.vazio = SimpleTextInput(hint_text="Peso da garrafa vazia", multiline=False)
        layout.add_widget(self.vazio)

        layout.add_widget(Label(text="Peso cheio (g):", font_size=sp(14), color=TEXT_PRIMARY, size_hint_y=None, height=dp(25)))
        self.cheio = SimpleTextInput(hint_text="Peso da garrafa cheia", multiline=False)
        layout.add_widget(self.cheio)

        layout.add_widget(Label(text="Volume total (mL):", font_size=sp(14), color=TEXT_PRIMARY, size_hint_y=None, height=dp(25)))
        self.volume = SimpleTextInput(hint_text="Volume da garrafa", multiline=False)
        layout.add_widget(self.volume)

        layout.add_widget(Widget(size_hint_y=None, height=dp(20)))

        btn_salvar = Button(
            text="SALVAR GARRAFA",
            font_size=sp(16),
            color=TEXT_PRIMARY,
            background_color=SUCCESS_COLOR,
            size_hint_y=None,
            height=dp(50)
        )
        btn_salvar.bind(on_press=self.salvar)
        layout.add_widget(btn_salvar)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def salvar(self, instance):
        n = self.nome.text.strip()
        if not n:
            self.app.mostrar_popup("Erro", "Nome obrigatório.")
            return
        try:
            v = float(self.vazio.text) if self.vazio.text else 0
            c = float(self.cheio.text) if self.cheio.text else 0
            vl = float(self.volume.text) if self.volume.text else 0
        except:
            self.app.mostrar_popup("Erro", "Preencha com números válidos.")
            return
        if v >= c:
            self.app.mostrar_popup("Erro", "Peso vazio deve ser < peso cheio.")
            return
        if vl <= 0:
            self.app.mostrar_popup("Erro", "Volume total deve ser > 0.")
            return

        massa_liquido = c - v
        densidade = massa_liquido / vl
        garrafas[n] = (v, c, vl, densidade)
        save_garrafas()

        self.nome.text = ""
        self.vazio.text = ""
        self.cheio.text = ""
        self.volume.text = ""

        self.app.mostrar_popup("Sucesso", f"✅ '{n}' cadastrada!")

        if hasattr(self.app, 'calculo_screen'):
            self.app.calculo_screen.atualizar_lista_garrafas()


class ExclusaoScreen(Screen):
    """Tela de exclusão de garrafas"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.build_ui()

    def build_ui(self):
        scroll = ScrollView()
        layout = BoxLayout(orientation="vertical", padding=[dp(20), dp(15), dp(20), dp(15)], spacing=dp(15), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        layout.add_widget(Label(
            text="🗑️ EXCLUIR GARRAFA",
            font_size=sp(20),
            color=DANGER_COLOR,
            size_hint_y=None,
            height=dp(50),
            bold=True,
            halign='center'
        ))

        layout.add_widget(Widget(size_hint_y=None, height=dp(30)))

        layout.add_widget(Label(text="Selecione a garrafa:", font_size=sp(14), color=TEXT_PRIMARY, size_hint_y=None, height=dp(25)))

        self.spinner = Spinner(
            text="",
            values=[],
            size_hint_y=None,
            height=dp(50),
            font_size=sp(14),
            background_color=BG_INPUT,
            color=TEXT_PRIMARY
        )
        layout.add_widget(self.spinner)

        layout.add_widget(Label(text="Informações:", font_size=sp(14), color=TEXT_PRIMARY, size_hint_y=None, height=dp(25)))

        scroll_info = ScrollView(size_hint_y=None, height=dp(120))
        self.info_label = Label(
            text="",
            font_size=sp(12),
            color=TEXT_SECONDARY,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.info_label.bind(texture_size=self.info_label.setter('size'))
        scroll_info.add_widget(self.info_label)
        layout.add_widget(scroll_info)

        layout.add_widget(Widget(size_hint_y=None, height=dp(20)))

        btn_excluir = Button(
            text="EXCLUIR GARRAFA",
            font_size=sp(16),
            color=TEXT_PRIMARY,
            background_color=DANGER_COLOR,
            size_hint_y=None,
            height=dp(50)
        )
        btn_excluir.bind(on_press=self.confirmar_exclusao)
        layout.add_widget(btn_excluir)

        scroll.add_widget(layout)
        self.add_widget(scroll)
        self.atualizar_lista()

    def on_enter(self):
        self.atualizar_lista()

    def atualizar_lista(self):
        lista = sorted(garrafas.keys())
        self.spinner.values = lista
        if lista:
            self.spinner.text = lista[0]
            self.atualizar_info(self.spinner.text)
        else:
            self.spinner.text = ""
            self.info_label.text = "Nenhuma garrafa cadastrada"

        self.spinner.bind(text=self.on_spinner_select)

    def on_spinner_select(self, spinner, text):
        self.atualizar_info(text)

    def atualizar_info(self, nome):
        if nome in garrafas:
            peso_vazio, peso_cheio, volume_total, densidade = garrafas[nome]
            self.info_label.text = f"📦 {nome}\n\n⚖️ Peso vazio: {peso_vazio:.0f}g\n⚖️ Peso cheio: {peso_cheio:.0f}g\n🧪 Volume total: {volume_total:.0f}mL\n📊 Densidade: {densidade:.3f}g/mL"

    def confirmar_exclusao(self, instance):
        if not self.spinner.text:
            self.app.mostrar_popup("Atenção", "Nenhuma garrafa para excluir.")
            return

        nome = self.spinner.text

        content = BoxLayout(orientation="vertical", spacing=dp(15), padding=dp(15))
        content.add_widget(Label(
            text=f"⚠️ Tem certeza que deseja\nexcluir a garrafa '{nome}'?\n\nEsta ação não pode ser desfeita.",
            font_size=sp(14),
            color=DANGER_COLOR,
            halign='center'
        ))

        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))

        def excluir(instance):
            del garrafas[nome]
            save_garrafas()
            self.atualizar_lista()
            confirm_popup.dismiss()
            self.app.mostrar_popup("Sucesso", f"✅ Garrafa '{nome}' removida!")

            if hasattr(self.app, 'calculo_screen'):
                self.app.calculo_screen.atualizar_lista_garrafas()
                if not garrafas:
                    self.app.calculo_screen.nome_garrafa.text = ""

        btn_sim = Button(
            text="SIM, EXCLUIR",
            background_color=DANGER_COLOR,
            color=TEXT_PRIMARY,
            size_hint_x=0.5,
            size_hint_y=None,
            height=dp(45)
        )
        btn_sim.bind(on_press=excluir)

        btn_nao = Button(
            text="CANCELAR",
            background_color=get_color_from_hex('#95A5A6'),
            color=TEXT_PRIMARY,
            size_hint_x=0.5,
            size_hint_y=None,
            height=dp(45)
        )
        btn_nao.bind(on_press=lambda x: confirm_popup.dismiss())

        btn_box.add_widget(btn_sim)
        btn_box.add_widget(btn_nao)
        content.add_widget(btn_box)

        confirm_popup = Popup(
            title="CONFIRMAR EXCLUSÃO",
            content=content,
            size_hint=(0.85, 0.45),
            auto_dismiss=False,
            background_color=BG_CARD,
            title_color=TEXT_PRIMARY
        )
        confirm_popup.open()


class CalculadoraDosesApp(App):
    def build(self):
        self.title = "Calculadora de Doses"

        self.screen_manager = ScreenManager()

        self.calculo_screen = CalculoScreen(name='calculo')
        cadastro_screen = CadastroScreen(name='cadastro')
        exclusao_screen = ExclusaoScreen(name='exclusao')

        self.screen_manager.add_widget(self.calculo_screen)
        self.screen_manager.add_widget(cadastro_screen)
        self.screen_manager.add_widget(exclusao_screen)

        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(self.screen_manager)

        self.bottom_nav = BottomNavBar(self.screen_manager)
        main_layout.add_widget(self.bottom_nav)

        return main_layout

    def mostrar_popup(self, titulo, msg):
        content = BoxLayout(orientation="vertical", spacing=dp(15), padding=dp(15))
        content.add_widget(Label(
            text=msg,
            font_size=sp(14),
            halign='center',
            size_hint_y=None,
            height=dp(60),
            color=TEXT_PRIMARY
        ))

        btn = Button(
            text="OK",
            size_hint_y=None,
            height=dp(45),
            background_color=PRIMARY_COLOR,
            color=TEXT_PRIMARY
        )
        popup = Popup(
            title=titulo,
            content=content,
            size_hint=(0.8, 0.35),
            auto_dismiss=False,
            background_color=BG_CARD,
            title_color=TEXT_PRIMARY
        )
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()


if __name__ == "__main__":
    load_garrafas()
    CalculadoraDosesApp().run()
