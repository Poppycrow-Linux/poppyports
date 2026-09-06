# config.py
import configparser
import os
from dataclasses import dataclass, fields
from .logutil import State, StateBenchmark, human_fsize


@dataclass
class Config:
    portsdir: str = "./recipes"
    append_portsdir: bool = True
    builddir: str = "./build"
    target: str | None = None
    sysroot: str | None = None
    sysroot_path: str | None = None
    toolchain: str | None = None

    ignore_integrity: bool = False
    redownload: bool = False
    rebuild: bool = False

    color: bool = True
    suppress_non_error_logs: bool = False
    show_build_breakdown: bool = True

    # things below are cli only options
    sign_key: str | None = None
    pkgpath: str | None = None


FIELD_TO_SECTION = {
    "portsdir": "Build",
    "append_portsdir": "Build",
    "default_builddir": "Build",
    "target": "Build",
    "sysroot": "Build",
    "sysroot_path": "Build",
    "toolchain": "Build",
    "ignore_integrity": "Build",
    "redownload": "Build",
    "rebuild": "Build",
    "color": "Display",
    "suppress_non_error_logs": "Display",
    "show_build_breakdown": "Display",
    "sign_key": None,
    "pkgpath": None
}


def _key(name: str) -> str: # turns snake case into camel case
    return "".join(p.capitalize() for p in name.split("_"))


def _ensure_config_file(path: str) -> None:
    cfg = configparser.ConfigParser()
    if os.path.exists(path):
        cfg.read(path)

    base = Config()
    for name, section in FIELD_TO_SECTION.items():
        if section is None:
            continue
        if not cfg.has_section(section):
            cfg.add_section(section)
        key = _key(name)
        if not cfg.has_option(section, key):
            default = getattr(base, name)
            if isinstance(default, bool):
                cfg.set(section, key, "yes" if default else "no")
            elif default is None:
                cfg.set(section, key, "")
            else:
                cfg.set(section, key, str(default))

    with open(path, "w") as f:
        cfg.write(f)


def _read_field(cfg: configparser.ConfigParser, name: str, default: Any) -> Any:
    key = _key(name)

    for section in cfg.sections():
        if cfg.has_option(section, key):
            if isinstance(default, bool):
                return cfg.getboolean(section, key)
            raw = cfg.get(section, key)
            if default is None or isinstance(default, str):
                v = raw.strip()
                return v if v else None if default is None else v
            return raw

    return default


def load_config(config_path: str, args: Any) -> Config: # this actually loads the config and applies
    _ensure_config_file(config_path)

    cfg = configparser.ConfigParser()
    cfg.read(config_path)

    base = Config()
    kwargs = {}

    for f in fields(Config):
        default = getattr(base, f.name)
        value = _read_field(cfg, f.name, default)

        cli = getattr(args, f.name, None)
        if cli is not None:
            value = cli

        kwargs[f.name] = value

    return Config(**kwargs)
