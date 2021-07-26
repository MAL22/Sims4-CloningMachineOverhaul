import enum


class Strings:

    class Interactions(enum.Int):
        CLONE_SETTINGS = 0x5E5A88DA
        AGE = 0x41B29A5B
        GENDER = 0x693D1836
        SEX = 0x752EE201
        FERTILITY = 0xE1F3ED25
        GENITALIA = 0x814746AB

    class GenderMenu(enum.Int):
        GENDER_MENU_TITLE = 0xF95F0C33
        GENDER_MENU_DESC = 0x39068824

    class BodySexMenu(enum.Int):
        BODY_SEX_MENU_TITLE = 0x5355410D
        BODY_SEX_MENU_DESC = 0xCF825E4C

    class AgeMenu(enum.Int):
        AGE_MENU_TITLE = 0x13262487
        AGE_MENU_DESC = 0x26C109D0

    class FertilityMenu(enum.Int):
        FERTILITY_MENU_TITLE = 0x743AFEC4
        FERTILITY_MENU_DESC = 0x07F12763
        CAN_BE_IMPREGNATED = 0x0
        CAN_IMPREGNATE = 0x0
        AUTOMATIC = 0x576B92FC
        NEITHER = 0
        BOTH = 0

    class GenitaliaMenu(enum.Int):
        GENITALIA_MENU_TITLE = 0xD1569BC2
        GENITALIA_MENU_DESC = 0xA773AF75

    class RelbitMenu(enum.Int):
        CMO_RELBIT_MENU_TITLE = 0xD588A7E2
        CMO_RELBIT_MENU_DESC = 0xB65E5700

    class ClothingPrefMenu(enum.Int):
        CMO_CLOTHING_PREF_MENU_TITLE = 0xCBD56826
        CMO_CLOTHING_PREF_MENU_DESC = 0x76D194A1

    class DnaPickerMenu(enum.Int):
        CMO_DNA_PICKER_DIALOG_TITLE = 0x0E556257
        CMO_DNA_PICKER_DIALOG_DESC = 0xC0529518

    class SimNameMenu(enum.Int):
        CMO_RENAME_SIM_DIALOG_TITLE = 0x3968E751
        CMO_RENAME_SIM_DIALOG_DESC = 0x9E93258A

    class GenericMenu(enum.Int):
        DEFAULT = 0xECD09801
        AUTOMATIC = 0x576B92FC
        NEITHER = 0
        BOTH = 0

    class Gender(enum.Int):
        MALE = 0x19E792E4
        FEMALE = 0x16B2C1D5
        AUTOMATIC = 0x576B92FC

    class Age(enum.Int):
        BABY = 0x150A4F1F
        TODDLER = 0x00F6323E
        CHILD = 0x4E7EBFE5
        TEEN = 0x45865C27
        YOUNGADULT = 0x7A68574A
        ADULT = 0xA95B08A9
        ELDER = 0xF7AFE1E1
        AUTOMATIC = 0x576B92FC

    class Relbit(enum.Int):
        SIBLING = 0x9536E86F
        OFFSPRING = 0x9BE2DBA5
        DEFAULT = 0xECD09801

    class VoiceTypes(enum.Int):
        VOICE_MELODIC = 0x4AAE3F32
        VOICE_SWEET = 0x289FA075
        VOICE_LILTED = 0xA59624F2
        VOICE_CLEAR = 0x56AD31D9
        VOICE_WARM = 0x1CC8C5D4
        VOICE_BRASH = 0x747E6B81

    class Affordances(enum.Int):
        CLONE_SETTINGS = 0x5E5A88DA
        AGE = 0x41B29A5B
        GENDER = 0x693D1836
        SEX = 0x752EE201
        FERTILITY = 0xE1F3ED25
        GENITALIA = 0x814746AB
