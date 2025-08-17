import asyncio, json, logging, os, datetime
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument

logging.basicConfig(format='[%(levelname)5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO)
CFG_PATH = os.environ.get("STOPVOICE_CONFIG","config.json")
cfg = {}

def load_cfg():
    global cfg
    with open(CFG_PATH,"r",encoding="utf-8") as f:
        cfg = json.load(f)
    for k,v in {"whitelist_ids":[],"whitelist_usernames":[],"owner_ids":[]}.items():
        if k not in cfg: cfg[k]=v
    cfg["whitelist_ids"]=set(int(x) for x in cfg.get("whitelist_ids",[]))
    cfg["owner_ids"]=set(int(x) for x in cfg.get("owner_ids",[]))
    cfg["whitelist_usernames"]=set(x.lower() for x in cfg.get("whitelist_usernames",[]))
    cfg["mode"]=cfg.get("mode","warn_then_delete")
    cfg["max_duration"]=int(cfg.get("max_duration",10))
    cfg["reply_text"]=cfg.get("reply_text","__Пользователь ограничил функцию голосовых сообщений.__")
    cfg["private_only"]=bool(cfg.get("private_only",True))
    cfg["enable"]=bool(cfg.get("enable",True))

def save_cfg():
    out = dict(cfg)
    out["whitelist_ids"]=sorted(list(int(x) for x in cfg["whitelist_ids"]))
    out["owner_ids"]=sorted(list(int(x) for x in cfg["owner_ids"]))
    out["whitelist_usernames"]=sorted(list(cfg["whitelist_usernames"]))
    for k in ("api_id","api_hash","session","phone","mode","max_duration","reply_text","private_only","enable"):
        out[k]=cfg.get(k,out.get(k))
    with open(CFG_PATH,"w",encoding="utf-8") as f:
        json.dump(out,f,ensure_ascii=False,indent=2)

def is_owner(uid:int)->bool:
    return uid in cfg["owner_ids"]

def voice_duration(msg):
    m = msg
    if isinstance(getattr(m,"media",None),MessageMediaDocument):
        v = getattr(m,"voice",None)
        if v is None and hasattr(m,"media") and hasattr(m.media,"document"):
            for a in getattr(m.media.document,"attributes",[]):
                if getattr(a,"voice",False):
                    return int(getattr(a,"duration",0) or 0)
        if v and hasattr(v,"attributes"):
            for a in v.attributes:
                if getattr(a,"voice",False):
                    return int(getattr(a,"duration",0) or 0)
    v = getattr(m,"voice",None)
    if v and hasattr(v,"attributes"):
        for a in v.attributes:
            if getattr(a,"voice",False):
                return int(getattr(a,"duration",0) or 0)
    return None

def should_act(dur:int)->bool:
    return dur is not None and dur < cfg["max_duration"]

async def resolve_user_id(client, token:str):
    token = token.strip()
    if token.startswith("@"):
        try:
            ent = await client.get_entity(token)
            return int(ent.id), ent.username.lower() if getattr(ent,"username",None) else None
        except Exception:
            return None, None
    try:
        uid = int(token)
        ent = await client.get_entity(uid)
        return int(ent.id), ent.username.lower() if getattr(ent,"username",None) else None
    except Exception:
        return None, None

def fmt_status():
    return (
        f"Статус: {'ON' if cfg['enable'] else 'OFF'}\n"
        f"Режим: {cfg['mode']}\n"
        f"Порог: {cfg['max_duration']} c\n"
        f"Только личные чаты: {cfg['private_only']}\n"
        f"WL IDs: {len(cfg['whitelist_ids'])}\n"
        f"WL usernames: {len(cfg['whitelist_usernames'])}"
    )

load_cfg()
client = TelegramClient(cfg.get("session","session"), int(cfg["api_id"]), cfg["api_hash"])

@client.on(events.NewMessage(incoming=True))
async def on_message(event):
    try:
        if not cfg["enable"]:
            return
        if cfg["private_only"] and not event.is_private:
            return
        dur = voice_duration(event.message)
        if dur is None:
            return
        s = await event.get_sender()
        if s and (int(s.id) in cfg["whitelist_ids"] or (getattr(s,"username",None) and s.username.lower() in cfg["whitelist_usernames"])):
            return
        if not should_act(dur):
            return
        mode = cfg["mode"]
        if mode == "warn_then_delete":
            try:
                await event.respond(cfg["reply_text"])
            except Exception:
                pass
            try:
                await client.delete_messages(event.chat_id,[event.id])
            except Exception:
                pass
        elif mode == "warn_only":
            await event.respond(cfg["reply_text"])
        elif mode == "delete_only":
            await client.delete_messages(event.chat_id,[event.id])
        elif mode == "off":
            return
    except Exception:
        logging.exception("on_message")

@client.on(events.NewMessage(pattern=r'^/(allow|deny|set|mode|status|reload|enable|disable|wl)\b', incoming=True))
async def on_command(event):
    try:
        if not event.is_private:
            return
        sender = await event.get_sender()
        if not is_owner(int(sender.id)):
            return
        text = event.raw_text.strip()
        parts = text.split(maxsplit=2)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts)>1 else ""
        if cmd == "/allow":
            if not arg:
                await event.reply("Укажи @username или id")
                return
            uid, uname = await resolve_user_id(client, arg)
            if uid is None and arg.startswith("@"):
                cfg["whitelist_usernames"].add(arg[1:].lower())
                save_cfg()
                await event.reply(f"Добавлен в WL username {arg.lower()}")
                return
            if uid is None:
                await event.reply("Пользователь не найден")
                return
            cfg["whitelist_ids"].add(int(uid))
            if uname: cfg["whitelist_usernames"].add(uname)
            save_cfg()
            await event.reply(f"Добавлен в WL id {uid}" + (f", @{uname}" if uname else ""))
        elif cmd == "/deny":
            if not arg:
                await event.reply("Укажи @username или id")
                return
            removed = []
            if arg.startswith("@"):
                u = arg[1:].lower()
                if u in cfg["whitelist_usernames"]:
                    cfg["whitelist_usernames"].discard(u)
                    removed.append(f"@{u}")
                uid, uname = await resolve_user_id(client, arg)
                if uid is not None and uid in cfg["whitelist_ids"]:
                    cfg["whitelist_ids"].discard(int(uid))
                    removed.append(str(uid))
            else:
                try:
                    uid = int(arg)
                    if uid in cfg["whitelist_ids"]:
                        cfg["whitelist_ids"].discard(uid)
                        removed.append(str(uid))
                except Exception:
                    pass
            save_cfg()
            await event.reply("Удалено: " + (", ".join(removed) if removed else "ничего"))
        elif cmd == "/set":
            try:
                val = int(arg)
                if val<=0 or val>300:
                    await event.reply("Порог 1..300")
                    return
                cfg["max_duration"]=val
                save_cfg()
                await event.reply(f"Порог обновлён: {val} c")
            except Exception:
                await event.reply("Укажи число секунд")
        elif cmd == "/mode":
            m = arg.strip().lower()
            if m not in {"warn_then_delete","warn_only","delete_only","off"}:
                await event.reply("Доступно: warn_then_delete | warn_only | delete_only | off")
                return
            cfg["mode"]=m
            save_cfg()
            await event.reply(f"Режим: {m}")
        elif cmd == "/status":
            await event.reply(fmt_status())
        elif cmd == "/reload":
            load_cfg()
            await event.reply("Конфиг перезагружен\n"+fmt_status())
        elif cmd == "/enable":
            cfg["enable"]=True
            save_cfg()
            await event.reply("Включено")
        elif cmd == "/disable":
            cfg["enable"]=False
            save_cfg()
            await event.reply("Выключено")
        elif cmd == "/wl":
            ids = sorted(list(cfg["whitelist_ids"]))
            uns = sorted(list(cfg["whitelist_usernames"]))
            txt = "WL IDs: " + (", ".join(str(x) for x in ids) if ids else "—") + "\nWL usernames: " + (", ".join("@"+x for x in uns) if uns else "—")
            await event.reply(txt)
    except Exception:
        logging.exception("on_command")

async def _main():
    await client.start(cfg.get("phone"))
    me = await client.get_me()
    if not cfg["owner_ids"]:
        cfg["owner_ids"] = {int(me.id)}
        save_cfg()
    logging.info("Started as %s (%s)", me.first_name, me.id)
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(_main())
