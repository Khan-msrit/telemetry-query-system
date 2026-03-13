from app.parser.rule_parser import parse_rule_based

print(parse_rule_based("average BUS_VOL"))
print(parse_rule_based("compare BUS_VOL and BAT_VOL_M_FINE"))
print(parse_rule_based("show BUS_VOL"))
print(parse_rule_based("how many times was RCSL active"))
