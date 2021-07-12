import enum


class Sex(enum.Int):
    AUTOMATIC = 0
    MALE = 136877
    FEMALE = 136878


class Genitalia(enum.Int):
    AUTOMATIC = 0
    MALE = 136876
    FEMALE = 137718


class Fertility(enum.Int):
    AUTOMATIC = 0
    BOTH = 1
    NEITHER = 2
    CAN_IMPREGNATE = 136874
    CAN_BE_IMPREGNATED = 136875


class MaleFertility(enum.Int):
    AUTOMATIC = 0
    CAN_IMPREGNATE = 136874
    CANNOT_IMPREGNATE = 137717


class FemaleFertility(enum.Int):
    AUTOMATIC = 0
    CAN_BE_IMPREGNATED = 136875
    CANNOT_BE_IMPREGNATED = 137716


class SexualPreference(enum.Int):
    AUTOMATIC = 0
    HETEROSEXUAL = 1
    HOMOSEXUAL = 2
    BISEXUAL = 3


class RelationshipBit(enum.Int):
    NONE = 0
    SIBLING = 8802
    OFFSPRING = 8805


class VoiceActor(enum.Int):
    AUTOMATIC = 0
    MELODIC = 1802970399
    SWEET = 1802970394
    LILTED = 1802970392
    CLEAR = 1685527063
    WARM = 1685527060
    BRASH = 1685527061


class VoiceEffect(enum.Int):
    AUTOMATIC = 0
    ALIEN = 957313736041630322
    SERVO = 17043571781846828025
