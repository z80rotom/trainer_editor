from tkinter import *
from tkinter import ttk
from dataclasses import dataclass
import dataclasses
import json
import copy
from collections import OrderedDict

@dataclass
class TrainerType:
    TrainerID: int

@dataclass
class TrainerPokemon:
    MonsNo: int
    FormNo: int
    IsRare: int # Shiny
    Level: int
    Sex: int
    Item: int
    Seikaku: int # Nature?
    Tokusei: int # Ability?
    Ball: int
    Seal: int
    Waza1: int
    Waza2: int
    Waza3: int
    Waza4: int
    TalentHp: int # IV
    TalentAtk: int
    TalentDef: int
    TalentSpAtk: int
    TalentSpDef: int
    TalentAgi: int
    EffortHp: int # EV
    EffortAtk: int
    EffortDef: int
    EffortSpAtk: int
    EffortSpDef: int
    EffortAgi: int

@dataclass
class TrainerParty:
    ID: int
    party: list

    def serialize(self):
        retVal = {}
        retVal["ID"] = self.ID

        for i, partyMember in enumerate(self.party):
            entry = {}
            for key, value in dataclasses.asdict(partyMember).items():
                entry["P{}{}".format(i, key)] = value
            retVal.update(entry)
        return retVal

@dataclass
class TrainerData:
    TypeID: int
    ColorID: int
    FightType: int
    ArenaID: int
    EffectID: int
    Gold: int
    UseItem1: int
    UseItem2: int
    UseItem3: int
    UseItem4: int
    HpRecoverFlag: int
    GiftItem: int
    NameLabel: str
    MsgFieldPokeOne: str
    MsgFieldBefore: str
    MsgFieldRevenge: str
    MsgFieldAfter: str
    MsgBattle: list
    SeqBattle: list
    AIBit: int


class GLocale:
    locale_info = {}

    @staticmethod
    def parse_locale_obj(data):
        locale_info = {}
        labelDataArray = data["labelDataArray"]
        for labelData in labelDataArray:
            labelName = labelData["labelName"]
            wordDataArray = labelData["wordDataArray"]
            localized_label = "".join([wordData["str"].encode("ascii", "ignore").decode() for wordData in wordDataArray])
            locale_info[labelName] = localized_label.replace("\n", "").replace("\r", "")
        return locale_info

    @classmethod
    def load_locale(cls, ifpath):
        with open(ifpath, "rb") as ifobj:
            locale_obj = json.load(ifobj)
            cls.locale_info.update(cls.parse_locale_obj(locale_obj))
        return cls.locale_info

    @classmethod
    def getLocalized(cls, label):
        return cls.locale_info[label]

    @classmethod
    def getPokemonName(cls, monsNo):
        return cls.getLocalized("MONSNAME_{:03d}".format(monsNo))

    @classmethod
    def getAbilityName(cls, abilityNo):
        return cls.getLocalized("TOKUSEI_{:03d}".format(abilityNo))

    @classmethod
    def getTypeName(cls, typeNo):
        if typeNo >= 9:
            return cls.getLocalized("TYPENAME_{:03d}".format(typeNo+1))
        return cls.getLocalized("TYPENAME_{:03d}".format(typeNo))
    
    @classmethod
    def getItemName(cls, itemNo):
        return cls.getLocalized("ITEMNAME_{:03d}".format(itemNo))
    
    @classmethod
    def getMoveName(cls, wazaNo):
        return cls.getLocalized("WAZANAME_{:03d}".format(wazaNo))

class GDataManager:
    MOVE_LIST = []
    POKEMON_LIST = []
    ITEM_LIST = []
    NATURE_LIST = []
    ABILITY_LIST = []
    TRAINER_MSG_LIST = []
    TRAINER_NAMES = OrderedDict()
    TRAINER_NAMES_REVERSE = OrderedDict()
    TRAINER_DATA = []
    TRAINER_POKE = []

    @classmethod
    def getMoveById(cls, moveId):
        move_list = cls.getMoveList()
        return move_list[moveId]

    @classmethod
    def getMoveList(cls):
        # TODO: Base this off of WazaTable instead
        if not cls.MOVE_LIST:
            with open("AssetFolder/english_Export/english_ss_wazaname.json", "r", encoding='utf-8') as ifobj:
                data = json.load(ifobj)
                for i, entry in enumerate(data["labelDataArray"]):
                    labelName = int(entry["labelName"].replace("WAZANAME_", ""))
                    if labelName != i:
                        print("Warning Bad Data: {} != {}".format(labelName, i))
                    string = entry["wordDataArray"][0]["str"]
                    string = string.encode('utf-8')
                    string = string.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'-')
                    string = string.decode('utf-8')
                    cls.MOVE_LIST.append(string)
        return cls.MOVE_LIST    

    @classmethod
    def getPokemonById(cls, pokemonId):
        pokemon_list = cls.getPokemonList()
        return pokemon_list[pokemonId]

    @classmethod
    def getPokemonList(cls):
        if not cls.POKEMON_LIST:
            with open("AssetFolder/common_msbt_Export/english_ss_monsname.json", "r", encoding='utf-8') as ifobj:
                data = json.load(ifobj)
                for i, entry in enumerate(data["labelDataArray"]):
                    labelName = int(entry["labelName"].replace("MONSNAME_", ""))
                    if labelName != i:
                        print("Warning Bad Data: {} != {}".format(labelName, i))
                    string = entry["wordDataArray"][0]["str"]
                    string = string.encode('utf-8')
                    string = string.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'-')
                    string = string.decode('utf-8')
                    cls.POKEMON_LIST.append(string)
        return cls.POKEMON_LIST 

    @classmethod
    def getItemById(cls, itemId):
        item_list = cls.getItemList()
        return item_list[itemId]

    @classmethod
    def getItemList(cls):
        if not cls.ITEM_LIST:
            with open("AssetFolder/english_Export/english_ss_itemname.json", "r", encoding='utf-8') as ifobj:
                data = json.load(ifobj)
                for i, entry in enumerate(data["labelDataArray"]):
                    if entry["labelName"] == "":
                        continue
                    string = entry["wordDataArray"][0]["str"]
                    string = string.encode('utf-8')
                    string = string.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'-')
                    string = string.decode('utf-8')
                    cls.ITEM_LIST.append(string)
        return cls.ITEM_LIST 

    @classmethod
    def getAbilityById(cls, abilityId):
        ability_list = cls.getAbilityList()
        return ability_list[abilityId]

    @classmethod
    def getAbilityList(cls):
        if not cls.ABILITY_LIST:
            with open("AssetFolder/english_Export/english_ss_tokusei.json", "r", encoding='utf-8') as ifobj:
                data = json.load(ifobj)
                for i, entry in enumerate(data["labelDataArray"]):
                    if entry["labelName"] == "":
                        continue
                    string = entry["wordDataArray"][0]["str"]
                    string = string.encode('utf-8')
                    string = string.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'-')
                    string = string.decode('utf-8')
                    cls.ABILITY_LIST.append(string)
        return cls.ABILITY_LIST 

    @classmethod
    def getNatureById(cls, natureId):
        nature_list = cls.getNatureList()
        return nature_list[natureId]

    @classmethod
    def getNatureList(cls):
        if not cls.NATURE_LIST:
            with open("AssetFolder/english_Export/english_ss_seikaku.json", "r", encoding='utf-8') as ifobj:
                data = json.load(ifobj)
                for i, entry in enumerate(data["labelDataArray"]):
                    if entry["labelName"] == "":
                        continue
                    string = entry["wordDataArray"][0]["str"]
                    string = string.encode('utf-8')
                    string = string.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'-')
                    string = string.decode('utf-8')
                    cls.NATURE_LIST.append(string)
        return cls.NATURE_LIST 

    @classmethod
    def getTrainerMessageList(cls):
        if not cls.TRAINER_MSG_LIST:
            with open("AssetFolder/english_Export/english_dp_trainer_msg.json", "r", encoding='utf-8') as ifobj:
                data = json.load(ifobj)
                for i, entry in enumerate(data["labelDataArray"]):
                    labelName = entry["labelName"]
                    if labelName == "":
                        continue
                    cls.TRAINER_MSG_LIST.append(labelName)
        return cls.TRAINER_MSG_LIST

    @classmethod
    def getTrainerNameByLabel(cls, labelName):
        trainer_names = cls.getTrainerNames()
        return trainer_names[labelName]

    @classmethod
    def getTrainerNameLabelByName(cls, name):
        cls.getTrainerNames()
        return cls.TRAINER_NAMES_REVERSE[name]

    @classmethod
    def getTrainerNames(cls):
        if not cls.NATURE_LIST:
            with open("AssetFolder/english_Export/english_dp_trainers_name.json", "r", encoding='utf-8') as ifobj:
                data = json.load(ifobj)
                for i, entry in enumerate(data["labelDataArray"]):
                    labelName = entry["labelName"]
                    if entry["labelName"] == "":
                        continue
                    string = entry["wordDataArray"][0]["str"]
                    string = string.encode('utf-8')
                    string = string.replace(b'\xc3\xa2\xe2\x82\xac\xe2\x80\x9d', b'-')
                    string = string.decode('utf-8')
                    cls.TRAINER_NAMES[labelName] = string
                    cls.TRAINER_NAMES_REVERSE[string] = labelName
        return cls.TRAINER_NAMES 

    @classmethod
    def getTrainerTable(cls):
        if not cls.TRAINER_DATA and not cls.TRAINER_POKE:
            with open("AssetFolder/masterdatas_Export/TrainerTable.json", "r", encoding="utf-8") as ifobj:
                data = json.load(ifobj)
                trainerData = data["TrainerData"]
                trainerPoke = list(sorted(data["TrainerPoke"], key=lambda entry: entry["ID"]))
                cls.TRAINER_DATA = list(map(lambda trainerData: TrainerData(**trainerData), trainerData))
                def map_trainer_party(trainerPoke):
                    ID = None
                    pokemon = {}
                    party = []
                    for key, value in trainerPoke.items():
                        if key == "ID":
                            ID = value
                        if key.startswith("P"):
                            idx = int(key[1])
                            new_key = key[2:]
                            if idx not in pokemon:
                                pokemon[idx] = {}
                            pokemon[idx][new_key] = value
                    for idx in sorted(pokemon.keys()):
                        poke = pokemon[idx]
                        trainerPokeIt = TrainerPokemon(**poke)
                        party.append(trainerPokeIt)
                    return TrainerParty(ID=ID, party=party)
                cls.TRAINER_POKE = list(map(map_trainer_party, trainerPoke))

        return {
            "TrainerData" : cls.TRAINER_DATA,
            "TrainerPoke" : cls.TRAINER_POKE
        }

class IVSpinbox(ttk.Spinbox):
    def __init__(self, master, textvariable):
        super().__init__(master, textvariable=textvariable, from_=0, to=31)
        self.configure(validate="key", validatecommand=(self.register(self.key_validate), '%P'))

    def key_validate(self, new_value):
        if not new_value.isdigit():
            return False
        minval = self.config('from')[4]
        maxval = self.config('to')[4]
        if int(new_value) not in range(minval, maxval+1):
            return False
        return True

class EVSpinbox(ttk.Spinbox):
    def __init__(self, master, textvariable):
        super().__init__(master, textvariable=textvariable, from_=0, to=252)
        self.configure(validate="key", validatecommand=(self.register(self.key_validate), '%P'))
    
    def key_validate(self, new_value):
        if not new_value.isdigit():
            return False
        minval = self.config('from')[4]
        maxval = self.config('to')[4]
        if int(new_value) not in range(minval, maxval+1):
            return False
        return True

class LevelSpinbox(ttk.Spinbox):
    def __init__(self, master, textvariable):
        super().__init__(master, textvariable=textvariable, from_=1, to=99)
        self.configure(validate="key", validatecommand=(self.register(self.key_validate), '%P'))

    def key_validate(self, new_value):
        if not new_value.isdigit():
            return False
        minval = self.config('from')[4]
        maxval = self.config('to')[4]
        if int(new_value) not in range(minval, maxval+1):
            return False
        return True

class MoveOptionMenu(ttk.Combobox):
    def __init__(self, master, textvariable, **kwargs):
        move_list = sorted(set(GDataManager.getMoveList()))
        super().__init__(master, textvariable=textvariable, values=move_list, **kwargs)
        self.bind('<KeyRelease>', self.filterList)
    
    def filterList(self, event):
        value = event.widget.get()
        if value == '':
            return
        move_list = sorted(set(GDataManager.getMoveList()))
        self['values'] = list(filter(lambda move: move.lower().startswith(value.lower()), move_list))

class SpeciesOptionMenu(ttk.Combobox):
    def __init__(self, master, textvariable, **kwargs):
        pokemon_list = sorted(set(GDataManager.getPokemonList()))
        super().__init__(master, textvariable=textvariable, values=pokemon_list, **kwargs)
        self.bind('<KeyRelease>', self.filterList)
    
    def filterList(self, event):
        value = event.widget.get()
        if value == '':
            return
        pokemon_list = sorted(set(GDataManager.getPokemonList()))
        self['values'] = list(filter(lambda pokemon: pokemon.lower().startswith(value.lower()), pokemon_list))

class SexOptionMenu(ttk.OptionMenu):
    SEX_LIST = ["Default", "Male", "Female", "Agender"]
    def __init__(self, master, textvariable, **kwargs):
        super().__init__(master, textvariable, "Default", *self.SEX_LIST, **kwargs)
    #     self.bind('<KeyRelease>', self.filterList)
    
    # def filterList(self, event):
    #     value = event.widget.get()
    #     if value == '':
    #         return
    #     sex_list = ["Agender", "Male", "Female"]
    #     self['values'] = list(filter(lambda pokemon: pokemon.lower().startswith(value.lower()), pokemon_list))


class ItemOptionMenu(ttk.Combobox):
    def __init__(self, master, textvariable, **kwargs):
        item_list = sorted(set(GDataManager.getItemList()))
        super().__init__(master, textvariable=textvariable, values=item_list, **kwargs)
        self.bind('<KeyRelease>', self.filterList)
    
    def filterList(self, event):
        value = event.widget.get()
        if value == '':
            return
        item_list = sorted(set(GDataManager.getItemList()))
        self['values'] = list(filter(lambda item: item.lower().startswith(value.lower()), item_list))

class AbilityOptionMenu(ttk.Combobox):
    def __init__(self, master, textvariable, **kwargs):
        ability_list = sorted(set(GDataManager.getAbilityList()))
        super().__init__(master, textvariable=textvariable, values=ability_list, **kwargs)
        self.bind('<KeyRelease>', self.filterList)
    
    def filterList(self, event):
        value = event.widget.get()
        if value == '':
            return
        ability_list = sorted(set(GDataManager.getAbilityList()))
        self['values'] = list(filter(lambda ability: ability.lower().startswith(value.lower()), ability_list))

class NatureOptionMenu(ttk.Combobox):
    def __init__(self, master, textvariable, **kwargs):
        nature_list = sorted(set(GDataManager.getNatureList()))
        super().__init__(master, textvariable=textvariable, values=nature_list, **kwargs)
        self.bind('<KeyRelease>', self.filterList)
    
    def filterList(self, event):
        value = event.widget.get()
        if value == '':
            return
        nature_list = sorted(set(GDataManager.getNatureList()))
        self['values'] = list(filter(lambda nature: nature.lower().startswith(value.lower()), nature_list))

class TrainerNameOptionMenu(ttk.Combobox):
    def __init__(self, master, textvariable, **kwargs):
        trainer_names = sorted(set(GDataManager.getTrainerNames().values()))
        super().__init__(master, textvariable=textvariable, values=trainer_names, **kwargs)
        self.bind('<KeyRelease>', self.filterList)
    
    def filterList(self, event):
        value = event.widget.get()
        if value == '':
            return
        trainer_names = sorted(set(GDataManager.getTrainerNames().values()))
        self['values'] = list(filter(lambda name: name.lower().startswith(value.lower()), trainer_names))

class TrainerMessageOptionMenu(ttk.Combobox):
    def __init__(self, master, textvariable, **kwargs):
        trainer_msgs = sorted(set(GDataManager.getTrainerMessageList()))
        super().__init__(master, textvariable=textvariable, values=trainer_msgs, width=50, **kwargs)
        self.bind('<KeyRelease>', self.filterList)
    
    def filterList(self, event):
        value = event.widget.get()
        if value == '':
            return
        trainer_msgs = sorted(set(GDataManager.getTrainerMessageList()))
        self['values'] = list(filter(lambda trainer_msg: trainer_msg.lower().startswith(value.lower()), trainer_msgs))


class TrainerPartyFrame(ttk.Frame):
    def __init__(self, root, padding=10):
        super(self).__init__(root, padding=padding)

class TrainerPokemonFrame(ttk.Frame):
    def __init__(self, root, pokeIndex, trainerPokemon, padding=3):
        super().__init__(root, padding=padding)
        self.pokeIndex = pokeIndex
        self.trainerPokemon = trainerPokemon
        self.effortHp = StringVar(self, self.trainerPokemon.EffortHp, "P{}EffortHp".format(self.pokeIndex))
        self.effortAtk = StringVar(self, self.trainerPokemon.EffortAtk, "P{}EffortAtk".format(self.pokeIndex))
        self.effortDef = StringVar(self, self.trainerPokemon.EffortDef, "P{}EffortDef".format(self.pokeIndex))
        self.effortSpAtk = StringVar(self, self.trainerPokemon.EffortSpAtk, "P{}EffortSpAtk".format(self.pokeIndex))
        self.effortSpDef = StringVar(self, self.trainerPokemon.EffortSpDef, "P{}EffortSpDef".format(self.pokeIndex))
        self.effortAgi = StringVar(self, self.trainerPokemon.EffortAgi, "P{}EffortAgi".format(self.pokeIndex))
        # self.effortHp.trace_add("write")

        self.evs = [{
            "name" : "Hp",
            "stringVar" : self.effortHp
        }, {
            "name" : "Atk",
            "stringVar" : self.effortAtk
        }, {
            "name" : "Def",
            "stringVar" : self.effortDef
        }, {
            "name" : "SpAtk",
            "stringVar" : self.effortSpAtk
        }, {
            "name" : "SpDef",
            "stringVar" : self.effortSpDef
        }, {
            "name" : "Agi",
            "stringVar" : self.effortAgi
        }]

        self.talentHp = StringVar(self, self.trainerPokemon.TalentHp, "P{}TalentHp".format(self.pokeIndex))
        self.talentAtk = StringVar(self, self.trainerPokemon.TalentAtk, "P{}TalentAtk".format(self.pokeIndex))
        self.talentDef = StringVar(self, self.trainerPokemon.TalentDef, "P{}TalentDef".format(self.pokeIndex))
        self.talentSpAtk = StringVar(self, self.trainerPokemon.TalentSpAtk, "P{}TalentSpAtk".format(self.pokeIndex))
        self.talentSpDef = StringVar(self, self.trainerPokemon.TalentSpDef, "P{}TalentSpDef".format(self.pokeIndex))
        self.talentAgi = StringVar(self, self.trainerPokemon.TalentAgi, "P{}TalentAgi".format(self.pokeIndex))
        self.ivs = [{
            "name" : "Hp",
            "stringVar" : self.talentHp
        }, {
            "name" : "Atk",
            "stringVar" : self.talentAtk
        }, {
            "name" : "Def",
            "stringVar" : self.talentDef
        }, {
            "name" : "SpAtk",
            "stringVar" : self.talentSpAtk
        }, {
            "name" : "SpDef",
            "stringVar" : self.talentSpDef
        }, {
            "name" : "Agi",
            "stringVar" : self.talentAgi
        }]


        self.move1 = StringVar(self, GDataManager.getMoveById(self.trainerPokemon.Waza1), "P{}Waza1".format(self.pokeIndex))
        self.move2 = StringVar(self, GDataManager.getMoveById(self.trainerPokemon.Waza2), "P{}Waza2".format(self.pokeIndex))
        self.move3 = StringVar(self, GDataManager.getMoveById(self.trainerPokemon.Waza3), "P{}Waza3".format(self.pokeIndex))
        self.move4 = StringVar(self, GDataManager.getMoveById(self.trainerPokemon.Waza4), "P{}Waza4".format(self.pokeIndex))
        self.moves = [[{
            "name" : "Move 1",
            "stringVar" : self.move1
        }, {
            "name" : "Move 2",
            "stringVar" : self.move2
        }], [{
            "name" : "Move 3",
            "stringVar" : self.move3
        }, {
            "name" : "Move 4",
            "stringVar" : self.move4
        }]]

        self.miscFrame = ttk.Frame(self)
        # Row 0
        self.species = StringVar(self, GDataManager.getPokemonById(self.trainerPokemon.MonsNo), "P{}MonsNo".format(self.pokeIndex))
        self.formNo = StringVar(self, self.trainerPokemon.FormNo, "P{}FormNo".format(self.pokeIndex))
        self.speciesLabel = ttk.Label(self.miscFrame, text="Species")
        self.formNoLabel = ttk.Label(self.miscFrame, text="Form No.")
        self.speciesOptionMenu = SpeciesOptionMenu(self.miscFrame, self.species)
        self.formNoSpinBox = ttk.Spinbox(self.miscFrame, textvariable=self.formNo)

        # Row 1
        self.isRare = IntVar(self, self.trainerPokemon.IsRare, "P{}IsRare".format(self.pokeIndex))
        self.level = StringVar(self, self.trainerPokemon.Level, "P{}Level".format(self.pokeIndex))
        self.isRareLabel = ttk.Label(self.miscFrame, text="Shiny")
        self.levelLabel = ttk.Label(self.miscFrame, text="Level")
        self.isRareCheckbox = Checkbutton(self.miscFrame, variable=self.isRare)
        self.levelSpinBox = LevelSpinbox(self.miscFrame, self.level)

        # Row 2
        self.sex = StringVar(self, SexOptionMenu.SEX_LIST[self.trainerPokemon.Sex], "P{}Sex".format(self.pokeIndex))
        self.item = StringVar(self, GDataManager.getItemById(self.trainerPokemon.Item), "P{}Item".format(self.pokeIndex))
        self.sexLabel = ttk.Label(self.miscFrame, text="Sex")
        self.itemLabel = ttk.Label(self.miscFrame, text="Item")
        self.sexOptionMenu = SexOptionMenu(self.miscFrame, self.sex)
        self.itemOptionMenu = ItemOptionMenu(self.miscFrame, self.item)

        # Row 3
        self.ability = StringVar(self, GDataManager.getAbilityById(self.trainerPokemon.Tokusei), "P{}Tokusei".format(self.pokeIndex))
        self.nature = StringVar(self, GDataManager.getNatureById(self.trainerPokemon.Seikaku), "P{}Seikaku".format(self.pokeIndex))
        self.abilityLabel = ttk.Label(self.miscFrame, text="Ability")
        self.natureLabel = ttk.Label(self.miscFrame, text="Nature")
        self.abilityOptionMenu = AbilityOptionMenu(self.miscFrame, self.ability)
        self.natureOptionMenu = NatureOptionMenu(self.miscFrame, self.nature)

        # Row 4
        self.ball = StringVar(self, self.trainerPokemon.Ball, "P{}Ball".format(self.pokeIndex))
        self.seal = StringVar(self, self.trainerPokemon.Seal, "P{}Seal".format(self.pokeIndex))
        self.ballLabel = ttk.Label(self.miscFrame, text="Ball")
        self.sealLabel = ttk.Label(self.miscFrame, text="Seal")
        self.ballSpinBox = ttk.Spinbox(self.miscFrame, textvariable=self.ball)
        self.sealSpinBox = ttk.Spinbox(self.miscFrame, textvariable=self.seal)

        # Row 0
        self.speciesLabel.grid(column=0, row=0, padx=3, pady=3)
        self.speciesOptionMenu.grid(column=1, row=0, padx=3, pady=3)
        self.formNoLabel.grid(column=2, row=0, padx=3, pady=3)
        self.formNoSpinBox.grid(column=3, row=0, padx=3, pady=3)

        # Row 1
        self.isRareLabel.grid(column=0, row=1, padx=3, pady=3)
        self.isRareCheckbox.grid(column=1, row=1, padx=3, pady=3, sticky = 'w')
        self.levelLabel.grid(column=2, row=1, padx=3, pady=3)
        self.levelSpinBox.grid(column=3, row=1, padx=3, pady=3)

        # Row 2 
        self.sexLabel.grid(column=0, row=2, padx=3, pady=3)
        self.sexOptionMenu.grid(column=1, row=2, padx=3, pady=3)
        self.itemLabel.grid(column=2, row=2, padx=3, pady=3)
        self.itemOptionMenu.grid(column=3, row=2, padx=3, pady=3)

        # Row 3
        self.abilityLabel.grid(column=0, row=3, padx=3, pady=3)
        self.abilityOptionMenu.grid(column=1, row=3, padx=3, pady=3)
        self.natureLabel.grid(column=2, row=3, padx=3, pady=3)
        self.natureOptionMenu.grid(column=3, row=3, padx=3, pady=3)

        # Row 4
        self.ballLabel.grid(column=0, row=4, padx=3, pady=3)
        self.ballSpinBox.grid(column=1, row=4, padx=3, pady=3)
        self.sealLabel.grid(column=2, row=4, padx=3, pady=3)
        self.sealSpinBox.grid(column=3, row=4, padx=3, pady=3)

        self.miscFrame.grid(column=0, row=0, padx=3, pady=3, rowspan=5)

        # self.miscFrame = ttk.Frame(self)
        self.movesFrameLabel = ttk.Label(self, text="Moves")
        self.movesFrame = ttk.Frame(self, borderwidth=3, relief='sunken')
        for i, row in enumerate(self.moves):
            for j, col in enumerate(row):
                moveOptionMenu = MoveOptionMenu(self.movesFrame, col["stringVar"], 
                            validate="focusout", validatecommand=lambda: self.validateMoveOption(col["stringVar"]))
                moveOptionMenu.grid(column=j, row=i)
                 
        self.movesFrameLabel.grid(column=0, row=5, padx=3, pady=3, rowspan=1)
        self.movesFrame.grid(column=0, row=6, padx=3, pady=3, rowspan=2)
        self.grid_rowconfigure(6, weight=2, uniform="foo")

        self.evFrameLabel = ttk.Label(self, text="Effort Values")
        self.evFrame = ttk.Frame(self, borderwidth=3, relief='sunken')
        for i, ev in enumerate(self.evs):
            name = ev["name"]
            stringVar = ev["stringVar"]
            label = ttk.Label(self.evFrame, text=name)
            spinBox = EVSpinbox(self.evFrame, stringVar)
            label.grid(column=0, row=i, padx=3, pady=3)
            spinBox.grid(column=1, row=i, padx=3, pady=3)
        self.evFrameLabel.grid(column=1, row=0, padx=3, pady=3, rowspan=1)
        self.evFrame.grid(column=1, row=1, padx=3, pady=3, rowspan=7)


        self.ivFrameLabel = ttk.Label(self, text="Individual Values")
        self.ivFrame = ttk.Frame(self, borderwidth=3, relief='sunken')
        for i, iv in enumerate(self.ivs):
            name = iv["name"]
            stringVar = iv["stringVar"]
            label = ttk.Label(self.ivFrame, text=name)
            spinBox = IVSpinbox(self.ivFrame, stringVar)
            label.grid(column=0, row=i, padx=3, pady=3)
            spinBox.grid(column=1, row=i, padx=3, pady=3)
        # self.ivFrame.pack()
        self.ivFrameLabel.grid(column=2, row=0, padx=3, pady=3, rowspan=1)
        self.ivFrame.grid(column=2, row=1, padx=3, pady=3, rowspan=7)

        self.pack()

    def updateTrainerPokemon(self, trainerPokemon):
        self.trainerPokemon = trainerPokemon
        self.effortHp.set(self.trainerPokemon.EffortHp)
        self.effortAtk.set(self.trainerPokemon.EffortAtk)
        self.effortDef.set(self.trainerPokemon.EffortDef)
        self.effortSpAtk.set(self.trainerPokemon.EffortSpAtk)
        self.effortSpDef.set(self.trainerPokemon.EffortSpDef)
        self.effortAgi.set(self.trainerPokemon.EffortAgi)

        self.talentHp.set(self.trainerPokemon.TalentHp)
        self.talentAtk.set(self.trainerPokemon.TalentAtk)
        self.talentDef.set(self.trainerPokemon.TalentDef)
        self.talentSpAtk.set(self.trainerPokemon.TalentSpAtk)
        self.talentSpDef.set(self.trainerPokemon.TalentSpDef)
        self.talentAgi.set(self.trainerPokemon.TalentAgi)

        self.move1.set(GDataManager.getMoveById(self.trainerPokemon.Waza1))
        self.move2.set(GDataManager.getMoveById(self.trainerPokemon.Waza2))
        self.move3.set(GDataManager.getMoveById(self.trainerPokemon.Waza3))
        self.move4.set(GDataManager.getMoveById(self.trainerPokemon.Waza4))

        self.species.set(GDataManager.getPokemonById(self.trainerPokemon.MonsNo))
        self.formNo.set(self.trainerPokemon.FormNo)
        self.isRare.set(self.trainerPokemon.IsRare)
        self.level.set(self.trainerPokemon.Level)
        self.sex.set(SexOptionMenu.SEX_LIST[self.trainerPokemon.Sex])
        self.item.set(GDataManager.getItemById(self.trainerPokemon.Item))
        self.ability.set(GDataManager.getAbilityById(self.trainerPokemon.Tokusei))
        self.nature.set(GDataManager.getNatureById(self.trainerPokemon.Seikaku))
        self.ball.set(self.trainerPokemon.Ball)
        self.seal.set(self.trainerPokemon.Seal)

    def getTrainerPokemon(self):
        trainerPokemon = {
            "EffortHp" : int(self.effortHp.get()),
            "EffortAtk" : int(self.effortAtk.get()),
            "EffortDef" : int(self.effortDef.get()),
            "EffortSpAtk" : int(self.effortSpAtk.get()),
            "EffortSpDef" : int(self.effortSpDef.get()),
            "EffortAgi" : int(self.effortAgi.get()),

            "TalentHp" : int(self.talentHp.get()),
            "TalentAtk" : int(self.talentAtk.get()),
            "TalentDef" : int(self.talentDef.get()),
            "TalentSpAtk" : int(self.talentSpAtk.get()),
            "TalentSpDef" : int(self.talentSpDef.get()),
            "TalentAgi" : int(self.talentAgi.get()),
            "Waza1" : GDataManager.getMoveList().index(self.move1.get()),
            "Waza2" : GDataManager.getMoveList().index(self.move2.get()),
            "Waza3" : GDataManager.getMoveList().index(self.move3.get()),
            "Waza4" : GDataManager.getMoveList().index(self.move4.get()),
            "FormNo" : int(self.formNo.get()),
            "IsRare" : int(self.isRare.get()),
            "Level" : int(self.level.get()),
            "Sex" : SexOptionMenu.SEX_LIST.index(self.sex.get()),
            "Item" : GDataManager.getItemList().index(self.item.get()),
            "Seikaku" : GDataManager.getNatureList().index(self.nature.get()),
            "Tokusei" : GDataManager.getAbilityList().index(self.ability.get()),
            "MonsNo" : GDataManager.getPokemonList().index(self.species.get()),
            "Ball" : int(self.ball.get()),
            "Seal" : int(self.seal.get())
        }

        return TrainerPokemon(**trainerPokemon)

class TrainerPartyNotebook(ttk.Notebook):
    def __init__(self, master, trainerParty, padding=3):
        super().__init__(master, padding=padding)
        self.trainerParty = trainerParty
        self.p1 = TrainerPokemonFrame(self, 1, self.trainerParty.party[0])
        self.p2 = TrainerPokemonFrame(self, 2, self.trainerParty.party[1])
        self.p3 = TrainerPokemonFrame(self, 3, self.trainerParty.party[2])
        self.p4 = TrainerPokemonFrame(self, 4, self.trainerParty.party[3])
        self.p5 = TrainerPokemonFrame(self, 5, self.trainerParty.party[4])
        self.p6 = TrainerPokemonFrame(self, 6, self.trainerParty.party[5])
        
        self.add(self.p1, text="Pokemon 1")
        self.add(self.p2, text="Pokemon 2")
        self.add(self.p3, text="Pokemon 3")
        self.add(self.p4, text="Pokemon 4")
        self.add(self.p5, text="Pokemon 5")
        self.add(self.p6, text="Pokemon 6")

    def updateTrainerParty(self, trainerParty):
        self.trainerParty = trainerParty
        self.p1.updateTrainerPokemon(self.trainerParty.party[0])
        self.p2.updateTrainerPokemon(self.trainerParty.party[1])
        self.p3.updateTrainerPokemon(self.trainerParty.party[2])
        self.p4.updateTrainerPokemon(self.trainerParty.party[3])
        self.p5.updateTrainerPokemon(self.trainerParty.party[4])
        self.p6.updateTrainerPokemon(self.trainerParty.party[5])

    def getTrainerParty(self):
        trainerParty = copy.copy(self.trainerParty)
        trainerParty.party[0] = self.p1.getTrainerPokemon()
        trainerParty.party[1] = self.p2.getTrainerPokemon()
        trainerParty.party[2] = self.p3.getTrainerPokemon()
        trainerParty.party[3] = self.p4.getTrainerPokemon()
        trainerParty.party[4] = self.p5.getTrainerPokemon()
        trainerParty.party[5] = self.p6.getTrainerPokemon()
        return trainerParty

class TrainerDataFrame(ttk.Frame):
    def __init__(self, master, trainerData, padding=10):
        super().__init__(master)
        self.trainerData = trainerData

        self.coreDataFrame = Frame(self, borderwidth=3, relief='groove')
        self.messageFrame = Frame(self, borderwidth=3, relief='groove')

        self.msgFieldPokeOne = StringVar(self, self.trainerData.MsgFieldPokeOne, "MsgFieldPokeOne")
        self.msgFieldBefore = StringVar(self, self.trainerData.MsgFieldBefore, "MsgFieldBefore")
        self.msgFieldRevenge = StringVar(self, self.trainerData.MsgFieldRevenge, "MsgFieldRevenge")
        self.msgFieldAfter = StringVar(self, self.trainerData.MsgFieldAfter, "MsgFieldAfter")

        
        self.msgFightFirstDamage = StringVar(self, self.trainerData.MsgBattle[0], "MsgFightFirstDamage")
        self.msgFightPokeLast = StringVar(self, self.trainerData.MsgBattle[2], "MsgFightPokeLast")
        self.msgFightPokeLastHalfHp = StringVar(self, self.trainerData.MsgBattle[4], "MsgFightPokeLastHalfHp")
        self.msgFightLose = StringVar(self, self.trainerData.MsgBattle[6], "msgFightLose")

        self.msgs = [{
            "name" : "PokeOne",
            "stringVar" : self.msgFieldPokeOne
        }, {
            "name" : "Before",
            "stringVar" :  self.msgFieldBefore
        }, {
            "name" : "Revenge",
            "stringVar" : self.msgFieldRevenge
        }, {
            "name" : "After",
            "stringVar" : self.msgFieldAfter
        }, {
            "name" : "FightDamage",
            "stringVar" : self.msgFightFirstDamage
        }, {
            "name" : "PokeLast",
            "stringVar" : self.msgFightPokeLast
        }, {
            "name" : "PokeLastHalfHp",
            "stringVar" : self.msgFightPokeLastHalfHp
        }, {
            "name" : "Lose",
            "stringVar" : self.msgFightLose
        }]

        self.typeID = StringVar(self, self.trainerData.TypeID, "TypeID")
        self.trainerName = StringVar(self, GDataManager.getTrainerNameByLabel(self.trainerData.NameLabel), "NameLabel")
        self.hpRecoverFlag = IntVar(self, self.trainerData.HpRecoverFlag, "HpRecoverFlag")
        self.bossBattleFlag = IntVar(self, self.trainerData.SeqBattle == ['ee630'], "SeqBattle")
        self.gold = StringVar(self, self.trainerData.Gold, "Gold")
        self.aiBit = StringVar(self, self.trainerData.AIBit, "AIBit")
        self.colorID = StringVar(self, self.trainerData.ColorID, "ColorID")
        self.fightType = StringVar(self, self.trainerData.FightType, "FightType")
        self.arenaID = StringVar(self, self.trainerData.ArenaID, "ArenaID")
        self.effectID = StringVar(self, self.trainerData.EffectID, "EffectID")

        # Item Group
        self.useItem1 = StringVar(self, GDataManager.getItemById(self.trainerData.UseItem1), "UseItem1")
        self.useItem2 = StringVar(self, GDataManager.getItemById(self.trainerData.UseItem2), "UseItem2")
        self.useItem3 = StringVar(self, GDataManager.getItemById(self.trainerData.UseItem3), "UseItem3")
        self.useItem4 = StringVar(self, GDataManager.getItemById(self.trainerData.UseItem4), "UseItem4")
        self.giftItem = StringVar(self, GDataManager.getItemById(self.trainerData.GiftItem), "GiftItem")
        self.useItems = [{
            "name" : "Use Item 1",
            "stringVar" : self.useItem1
        }, {
            "name" : "Use Item 2",
            "stringVar" : self.useItem2
        }, {
            "name" : "Use Item 3",
            "stringVar" : self.useItem3
        }, {
            "name" : "Use Item 4",
            "stringVar" : self.useItem4
        }, {
            "name" : "Gift Item",
            "stringVar" : self.giftItem
        }]

        self.spinboxes = [{
            "name" : "AIBit",
            "stringVar" : self.aiBit
        }, {
            "name" : "Color ID",
            "stringVar" : self.colorID
        }, {
            "name" : "Fight Type",
            "stringVar" : self.fightType
        }, {
            "name" : "Arena ID",
            "stringVar" : self.arenaID
        }, {
            "name" : "Effect ID",
            "stringVar" : self.effectID
        }]

        self.typeIDLabel = ttk.Label(self.coreDataFrame, text="Type ID")
        self.typeIDSpinbox = ttk.Spinbox(self.coreDataFrame, textvariable=self.typeID)
        self.nameLabel = ttk.Label(self.coreDataFrame, text="Name")
        self.nameOptionMenu = TrainerNameOptionMenu(self.coreDataFrame, self.trainerName)

        self.hpRecoverFlagLabel = ttk.Label(self.coreDataFrame, text="HP Recover Flag")
        self.hpRecoverFlagCheckbox = Checkbutton(self.coreDataFrame, variable=self.hpRecoverFlag)
        self.bossBattleFlagLabel = ttk.Label(self.coreDataFrame, text="Boss Battle")
        self.bossBattleFlagCheckbox = Checkbutton(self.coreDataFrame, variable=self.bossBattleFlag)
        self.goldLabel = ttk.Label(self.coreDataFrame, text="Gold")
        self.goldSpinBox = ttk.Spinbox(self.coreDataFrame, textvariable=self.gold)

        for i, spinbox in enumerate(self.spinboxes):
            name = spinbox["name"]
            stringVar = spinbox["stringVar"]
            label = ttk.Label(self.coreDataFrame, text=name)
            spinbox = ttk.Spinbox(self.coreDataFrame, textvariable=stringVar)
            label.grid(column=0, row=i+1, padx=3, pady=3)
            spinbox.grid(column=1, row=i+1, padx=3, pady=3)

        for i, useItem in enumerate(self.useItems):
            name = useItem["name"]
            stringVar = useItem["stringVar"]
            label = ttk.Label(self.coreDataFrame, text=name)
            itemOptionMenu = ItemOptionMenu(self.coreDataFrame, stringVar)
            label.grid(column=2, row=i+2, padx=3, pady=3)
            itemOptionMenu.grid(column=3, row=i+2, padx=3, pady=3)

        for i, msg in enumerate(self.msgs):
            name = msg["name"]
            stringVar = msg["stringVar"]
            msgLabel = ttk.Label(self.messageFrame, text=name)
            msgOptionMenu = TrainerMessageOptionMenu(self.messageFrame, stringVar)     
            msgLabel.grid(column=0, row=i, padx=3, pady=3)
            msgOptionMenu.grid(column=1, row=i, padx=3, pady=3)
        self.messageFrame.grid_columnconfigure(0, weight=1, uniform="foo")
        self.messageFrame.grid_columnconfigure(1, weight=3, uniform="foo")

        # Row 0
        self.typeIDLabel.grid(column=0, row=0, padx=3, pady=3)
        self.typeIDSpinbox.grid(column=1, row=0, padx=3, pady=3)
        self.nameLabel.grid(column=2, row=0, padx=3, pady=3)
        self.nameOptionMenu.grid(column=3, row=0, padx=3, pady=3)

        # Row 1
        self.goldLabel.grid(column=2, row=1, padx=3, pady=3)
        self.goldSpinBox.grid(column=3, row=1, padx=3, pady=3)

        # Row 8
        self.hpRecoverFlagLabel.grid(column=0, row=8, padx=3, pady=3)
        self.hpRecoverFlagCheckbox.grid(column=1, row=8, padx=3, pady=3, sticky = 'w')
        self.bossBattleFlagLabel.grid(column=2, row=8, padx=3, pady=3)
        self.bossBattleFlagCheckbox.grid(column=3, row=8, padx=3, pady=3, sticky = 'w')

        # Internal Frames
        self.coreDataFrame.grid(column=0, row=0, padx=3, pady=3, columnspan=8)
        self.messageFrame.grid(column=8, row=0, padx=3, pady=3, columnspan=8)

    def getTrainerData(self):
        # self.trainerName.set(GDataManager.getTrainerNameByLabel(self.trainerData.NameLabel))
        msgBattle = []
        seqBattle = []
        if self.bossBattleFlag:
            seqBattle = ['ee630']
        
        if self.msgFightFirstDamage.get():
            msgBattle.append(self.msgFightFirstDamage.get())
            msgBattle.append('bk002')
        else:
            msgBattle.extend(['', ''])
        
        if self.msgFightPokeLast.get():
            msgBattle.append(self.msgFightPokeLast.get())
            msgBattle.append('bk002')
        else:
            msgBattle.extend(['', ''])
        
        if self.msgFightPokeLastHalfHp.get():
            msgBattle.append(self.msgFightPokeLastHalfHp.get())
            msgBattle.append('bk002')
        else:
            msgBattle.extend(['', ''])
                
        if self.msgFightLose.get():
            msgBattle.append(self.msgFightLose.get())
            msgBattle.append('bk002')
        else:
            msgBattle.extend(['', ''])
                
        msgBattle.append('ee501')

        trainerData = {
            "NameLabel" :  GDataManager.getTrainerNameLabelByName(self.trainerName.get()),
            "TypeID" : int(self.typeID.get()),
            "HpRecoverFlag" : int(self.hpRecoverFlag.get()),
            "Gold" : int(self.gold.get()),
            "AIBit" : int(self.aiBit.get()),
            "ColorID" : int(self.colorID.get()),
            "FightType" : int(self.fightType.get()),
            "ArenaID" : int(self.arenaID.get()),
            "EffectID" : int(self.effectID.get()),
            "MsgFieldPokeOne" : self.msgFieldPokeOne.get(),
            "MsgFieldBefore" : self.msgFieldBefore.get(),
            "MsgFieldRevenge" : self.msgFieldRevenge.get(),
            "MsgFieldAfter" : self.msgFieldAfter.get(),
            "MsgBattle" : msgBattle,
            "SeqBattle" : seqBattle,
            "UseItem1" : GDataManager.getItemList().index(self.useItem1.get()),
            "UseItem2" : GDataManager.getItemList().index(self.useItem2.get()),
            "UseItem3" : GDataManager.getItemList().index(self.useItem3.get()),
            "UseItem4" : GDataManager.getItemList().index(self.useItem4.get()),
            "GiftItem" : GDataManager.getItemList().index(self.giftItem.get()),
        }

        return TrainerData(**trainerData)

    def updateTrainerData(self, trainerData):
        self.trainerData = trainerData
        self.msgFieldPokeOne.set(self.trainerData.MsgFieldPokeOne)
        self.msgFieldBefore.set(self.trainerData.MsgFieldBefore)
        self.msgFieldRevenge.set(self.trainerData.MsgFieldRevenge)
        self.msgFieldAfter.set(self.trainerData.MsgFieldAfter)

        self.msgFightFirstDamage.set(self.trainerData.MsgBattle[0])
        self.msgFightPokeLast.set(self.trainerData.MsgBattle[2])
        self.msgFightPokeLastHalfHp.set(self.trainerData.MsgBattle[4])
        self.msgFightLose.set(self.trainerData.MsgBattle[6])

        self.typeID.set(self.trainerData.TypeID)
        self.trainerName.set(GDataManager.getTrainerNameByLabel(self.trainerData.NameLabel))
        self.hpRecoverFlag.set(self.trainerData.HpRecoverFlag)
        self.bossBattleFlag.set(self.trainerData.SeqBattle == ['ee630'])
        self.gold.set(self.trainerData.Gold)
        self.aiBit.set(self.trainerData.AIBit)
        self.colorID.set(self.trainerData.ColorID)
        self.fightType.set(self.trainerData.FightType)
        self.arenaID.set(self.trainerData.ArenaID)
        self.effectID.set(self.trainerData.EffectID)

        # Item Group
        self.useItem1.set(GDataManager.getItemById(self.trainerData.UseItem1))
        self.useItem2.set(GDataManager.getItemById(self.trainerData.UseItem2))
        self.useItem3.set(GDataManager.getItemById(self.trainerData.UseItem3))
        self.useItem4.set(GDataManager.getItemById(self.trainerData.UseItem4))
        self.giftItem.set(GDataManager.getItemById(self.trainerData.GiftItem))

class TrainerFrame(ttk.Frame):
    def __init__(self, master, padding=1):
        super().__init__(master, padding=padding)
        menubar = Menu(master)
        master.config(menu=menubar)
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Save", command=self.onSave)
        menubar.add_cascade(label="File", underline=0, menu=fileMenu)

        self.trainerTable = GDataManager.getTrainerTable()
        self.currIdx = 1
        
        self.treeViewFrame = ttk.Frame(self, borderwidth=3, relief='groove')
        self.containerFrame = ttk.Frame(self)
        self.treeView = ttk.Treeview(self.treeViewFrame, show='tree')
        self.ybar = Scrollbar(self.treeViewFrame, orient=VERTICAL, command=self.treeView.yview)
        self.treeView.configure(yscrollcommand=self.ybar.set)
        self.treeView.heading('#0', text='Trainers', anchor='w')
        self.treeView.bind('<ButtonRelease-1>', self.onTreeSelect)
        self.treeView.bind('<KeyRelease>', self.onTreeSelect)
        for i, trainerData in enumerate(self.trainerTable["TrainerData"]):
            trainerName = GDataManager.getTrainerNameByLabel(trainerData.NameLabel)
            nodeText = '{} - {}'.format(i, trainerName)
            self.treeView.insert('', 'end', text=nodeText, open=False)
        self.trainerDataFrame = TrainerDataFrame(self.containerFrame, self.trainerTable["TrainerData"][self.currIdx])
        self.trainerPartyNotebookFrame = ttk.Frame(self.containerFrame, borderwidth=3, relief='groove')
        self.trainerPartyNotebook = TrainerPartyNotebook(self.trainerPartyNotebookFrame, self.trainerTable["TrainerPoke"][self.currIdx])
        # GRID
        self.trainerDataFrame.pack(side=TOP, fill=X)
        self.trainerPartyNotebookFrame.pack(fill=X)

        # TreeView Frame Layout
        self.ybar.pack(side=RIGHT, fill=Y, expand=True)
        self.treeView.pack(fill=Y, expand=True)

        # 
        self.containerFrame.pack(side=RIGHT, fill=BOTH)
        self.treeViewFrame.pack(fill=Y, expand=True)

        # Trainer Party Notebook Frame Layout
        self.trainerPartyNotebook.pack(fill=BOTH, expand=True)
    
    def onSave(self):
        # Serialize updated TrainerParty into the map
        trainerData = self.trainerDataFrame.getTrainerData()
        trainerParty = self.trainerPartyNotebook.getTrainerParty()
        self.trainerTable["TrainerData"][self.currIdx] = trainerData
        self.trainerTable["TrainerPoke"][self.currIdx] = trainerParty
        fullTrainerTable = {}
        with open("AssetFolder/masterdatas_Export/TrainerTable.json", "r", encoding='utf-8') as ifobj:
            fullTrainerTable = json.load(ifobj)
        
        trainerData = list(map(lambda item: dataclasses.asdict(item), self.trainerTable["TrainerData"]))
        trainerPoke = list(map(lambda item: item.serialize(), self.trainerTable["TrainerPoke"]))
        fullTrainerTable["TrainerData"] = trainerData
        fullTrainerTable["TrainerPoke"] = trainerPoke

        with open("AssetFolder/masterdatas_Export/TrainerTable.json", "w", encoding='utf-8') as ofobj:
            json.dump(fullTrainerTable, ofobj, indent=4)

    def onTreeSelect(self, event):
        curItem = self.treeView.focus()
        newIdx = self.treeView.index(curItem)
        # Serialize updated TrainerParty into the map
        trainerData = self.trainerDataFrame.getTrainerData()
        trainerParty = self.trainerPartyNotebook.getTrainerParty()
        self.trainerTable["TrainerData"][self.currIdx] = trainerData
        self.trainerTable["TrainerPoke"][self.currIdx] = trainerParty
        # Set frames to use the new data
        self.currIdx = newIdx
        self.trainerDataFrame.updateTrainerData(self.trainerTable["TrainerData"][self.currIdx])
        self.trainerPartyNotebook.updateTrainerParty(self.trainerTable["TrainerPoke"][self.currIdx])
        

def gui_main():
    root = Tk()
    root.title("BDSP Trainer Editor")
    frm = TrainerFrame(root)
    frm.pack(expand=1, fill='both')
    root.mainloop()

if __name__ == "__main__":
    gui_main()