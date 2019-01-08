from core import chemicals, measurements

INDENT = " " * 4


def split_list(lst, n=3):
    i = len(lst) // n
    a = lst[: i + 1]
    b = lst[i + 1 : 2 * i + 2]
    c = lst[2 * i + 2 :]

    while len(c) < len(b):
        c.append("")

    return a, b, c


def choose_chemical(chems):
    chem_map = {i + 1: v.iri for i, v in enumerate(sorted(chems.values()))}

    items = ["{: >2}. {: <60} ".format(i, v) for i, v in chem_map.items()]

    for a, b, c in zip(*split_list(items)):
        print("{:<30}{:<30}{:<}".format(a, b, c))

    print()
    return chem_map.get(int(input("Choose a chemical: ")), None)


def choose_region(regions):
    region_map = {i + 1: v for i, v in enumerate(sorted(regions))}

    items = ["{: >2}. {: <60} ".format(i, v) for i, v in region_map.items()]

    for a, b, c in zip(*split_list(items)):
        print("{:<30}{:<30}{:<}".format(a, b, c))

    print()
    return region_map.get(int(input("Choose a region (0 for all): ")), None)


def print_info(chemical):
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    print()
    print(f"Chemical: {chemical.name}")
    try:
        print(f"{INDENT}Formula: {chemical.formula.translate(SUB)}")
    except:
        pass
    print(f"{INDENT}S-labels:")
    print(
        *[
            "{}{: >6}: {}".format(2 * INDENT, k.split(" ")[0], v)
            for k, v in chemical.s_labels.items()
        ],
        sep="\n",
    )
    print(f"{INDENT}R-labels:")
    print(
        *[
            "{}{: >6}: {}".format(2 * INDENT, k.split(" ")[0], v)
            for k, v in chemical.r_labels.items()
        ],
        sep="\n",
    )
    print()


def list_measurements(ms, fun=len, select_region=None, select_year=None):
    """List measurements for given chemical, aggregated by `fun`. If `region` is
    None, list for all regions. If `year` is None, list for all years."""

    print(f"measurementS ({len(ms)})")
    for region_group in measurements.group_by_region(ms):
        region = region_group[0].region
        if (region and select_region is None) or region == select_region:
            print(f"{INDENT}{region}")

            for year_group in measurements.group_by_year(region_group):
                year = int(year_group[0].year.split("-")[0])
                if select_year is None or select_year == year:
                    print(INDENT * 2, year, fun(year_group))


def total(group):
    return sum(m.value for m in group)


def run():
    all_chemicals = chemicals.get_all_chemicals()
    iri = choose_chemical(all_chemicals)
    print()

    chemical = all_chemicals[iri]

    ms = list(measurements.get_measurements(chemical))
    region = choose_region(measurements.get_regions(ms))

    print_info(chemical)
    list_measurements(ms, total, select_region=region)


try:
    run()
except KeyboardInterrupt:
    print("Stopped.")
    exit()
