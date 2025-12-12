# app/check.py
import re
from dataclasses import dataclass
from typing import List, Dict, Any
from .database import ClassT


@dataclass
class CheckError:
    code: int
    title: str
    have: int | None = None
    need: int | None = None
    lack: int | None = None
    detail: List[str] | None = None
    suggest: List[str] | None = None


def _to_credits(val) -> int:
    """'2' や '2単位' などから数字だけ抜く。無ければ0。"""
    if val is None:
        return 0
    m = re.search(r"\d+", str(val))
    return int(m.group()) if m else 0


def _names(rows: List[ClassT]) -> List[str]:
    return [r.kamokumei for r in rows]


def _sum_credits_acquired(rows: List[ClassT], is_acq, cap: int | None = None) -> int:
    """取得済みのみを合算。cap を渡すと上限を適用。"""
    s = sum(_to_credits(r.tani) for r in rows if is_acq(r.kamokumei))
    return min(s, cap) if cap is not None else s


def run_all_checks(session, user_id_str: str, uc_map: Dict[str, str]) -> Dict[str, Any]:
    """要件チェックを実行し、テンプレートに渡す dict を返す。"""
    errors: List[CheckError] = []
    TOTAL_NEED = 124

    q = lambda **kw: session.query(ClassT).filter_by(**kw).order_by(ClassT.id.asc()).all()
    is_acq = lambda name: uc_map.get(name) == "1"

    # ---------- チェック1：導入科目は全て必修 ----------
    do_list = q(k_kbn="導入科目")
    miss = [r.kamokumei for r in do_list if not is_acq(r.kamokumei)]
    if miss:
        errors.append(
            CheckError(
                1, "導入科目（必修）",
                have=len(do_list) - len(miss),
                need=len(do_list),
                lack=len(miss),
                detail=miss
            )
        )

    # 共通：各集合から1つ必須
    def need_one(code: int, title: str, rows: list[ClassT]):
        got = [r.kamokumei for r in rows if is_acq(r.kamokumei)]
        if len(got) < 1:
            errors.append(CheckError(code, title, have=len(got), need=1, lack=1 - len(got), suggest=_names(rows)))

    # ---------- チェック2～7：基礎の各カテゴリから1つ必須 ----------
    need_one(2, "基礎：基盤リテラシー（情報）から1つ",
             q(k_kbn="基礎科目", k_bunrui="基盤リテラシー科目", k_bunya="情報", nenji="1年次"))
    need_one(3, "基礎：基盤リテラシー（数理）から1つ",
             q(k_kbn="基礎科目", k_bunrui="基盤リテラシー科目", k_bunya="数理", nenji="1年次"))
    need_one(4, "基礎：多言語情報理解から1つ",
             q(k_kbn="基礎科目", k_bunrui="多言語情報理解科目", k_bunya="多言語情報理解", nenji="1年次"))
    need_one(5, "基礎：世界理解（文化・思想）から1つ",
             q(k_kbn="基礎科目", k_bunrui="世界理解科目", k_bunya="文化・思想", nenji="1年次"))
    need_one(6, "基礎：世界理解（社会・ネットワーク）から1つ",
             q(k_kbn="基礎科目", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク", nenji="1年次"))
    need_one(7, "基礎：世界理解（経済・マーケット）から1つ",
             q(k_kbn="基礎科目", k_bunrui="世界理解科目", k_bunya="経済・マーケット", nenji="1年次"))

    # ---------- チェック8：展開1デジタル産業の指定4科目から1つ必須 ----------
    specified = ["IT産業史", "マンガ産業史", "アニメ産業史", "日本のゲーム産業史"]
    got8 = [n for n in specified if is_acq(n)]
    if not got8:
        errors.append(CheckError(8, "展開1：デジタル産業（指定4科目のいずれか）", have=0, need=1, lack=1, suggest=specified))

    # ---------- チェック9：多言語情報理解（展開1+2）で6単位以上 ----------
    tag1 = q(k_kbn="展開科目", k_bunrui="多言語情報理解科目", k_bunya="多言語情報理解", nenji="1年次")
    tag2 = q(k_kbn="展開科目", k_bunrui="多言語情報理解科目", k_bunya="多言語情報理解", nenji="2年次")
    tag_all = tag1 + tag2
    c9 = _sum_credits_acquired(tag_all, is_acq, cap=None)
    if c9 < 6:
        errors.append(CheckError(9, "多言語情報理解（展開1+2）6単位以上", have=c9, need=6, lack=6 - c9, suggest=_names(tag_all)))

    # ---------- チェック10：基盤リテラシー（情報・数理）合計8単位以上 ----------
    sets10 = (
        q(k_kbn="基礎科目", k_bunrui="基盤リテラシー科目", k_bunya="情報", nenji="1年次") +
        q(k_kbn="基礎科目", k_bunrui="基盤リテラシー科目", k_bunya="数理", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="情報", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="数理", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="情報", nenji="2年次") +
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="数理", nenji="2年次") +
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="情報", nenji="3年次") +
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="数理", nenji="3年次") +
        q(k_kbn="展開科目（考究）", k_bunrui="基盤リテラシー科目", k_bunya="情報") +
        q(k_kbn="展開科目（考究）", k_bunrui="基盤リテラシー科目", k_bunya="数理")
    )
    c10 = _sum_credits_acquired(sets10, is_acq, cap=None)
    if c10 < 8:
        errors.append(CheckError(10, "基盤リテラシー（情報・数理）合計8単位以上", have=c10, need=8, lack=8 - c10, suggest=_names(sets10)))

    # ---------- チェック11：世界理解 合計26単位以上 ----------
    world_sets = (
        q(k_kbn="基礎科目", k_bunrui="世界理解科目", k_bunya="文化・思想", nenji="1年次") +
        q(k_kbn="基礎科目", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク", nenji="1年次") +
        q(k_kbn="基礎科目", k_bunrui="世界理解科目", k_bunya="経済・マーケット", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="文化・思想", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="経済・マーケット", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="デジタル産業", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="文化・思想", nenji="2年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク", nenji="2年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="経済・マーケット", nenji="2年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="デジタル産業", nenji="2年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="文化・思想", nenji="3年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク", nenji="3年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", k_bunya="デジタル産業", nenji="3年次") +
        q(k_kbn="展開科目（考究）", k_bunrui="世界理解科目", k_bunya="文化・思想") +
        q(k_kbn="展開科目（考究）", k_bunrui="世界理解科目", k_bunya="社会・ネットワーク") +
        q(k_kbn="展開科目（考究）", k_bunrui="世界理解科目", k_bunya="経済・マーケット") +
        q(k_kbn="展開科目（考究）", k_bunrui="世界理解科目", k_bunya="デジタル産業")
    )
    c11 = _sum_credits_acquired(world_sets, is_acq, cap=None)
    if c11 < 26:
        errors.append(CheckError(11, "世界理解 合計26単位以上", have=c11, need=26, lack=26 - c11, suggest=_names(world_sets)))

    # ===== 社会接続（展開1～3＋考究）セットと上限10の事前計算 =====
    shakai_plain = (
        q(k_kbn="展開科目", k_bunrui="社会接続科目", k_bunya="社会接続", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="社会接続科目", k_bunya="社会接続", nenji="2年次") +
        q(k_kbn="展開科目", k_bunrui="社会接続科目", k_bunya="社会接続", nenji="3年次")
    )
    shakai_kokyu = q(k_kbn="展開科目（考究）", k_bunrui="社会接続科目", k_bunya="社会接続")
    shakai_all = shakai_plain + shakai_kokyu

    shakai_raw = _sum_credits_acquired(shakai_all, is_acq, cap=None)  # 取得済みの“生”合計
    shakai_capped = min(shakai_raw, 10)                               # 計上上限10

    # ---------- チェック12：展開トータル 74単位以上（社会接続は上限10を適用） ----------
    sets12_except_shakai = (
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="情報", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="数理", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="多言語情報理解科目", k_bunya="多言語情報理解", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", nenji="1年次") +
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="情報", nenji="2年次") +
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="数理", nenji="2年次") +
        q(k_kbn="展開科目", k_bunrui="多言語情報理解科目", k_bunya="多言語情報理解", nenji="2年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", nenji="2年次") +
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="情報", nenji="3年次") +
        q(k_kbn="展開科目", k_bunrui="基盤リテラシー科目", k_bunya="数理", nenji="3年次") +
        q(k_kbn="展開科目", k_bunrui="世界理解科目", nenji="3年次") +
        q(k_kbn="展開科目（考究）", k_bunrui="基盤リテラシー科目") +
        q(k_kbn="展開科目（考究）", k_bunrui="世界理解科目")
        # ※ 社会接続（展開/考究）は除外
    )
    c12_except = _sum_credits_acquired(sets12_except_shakai, is_acq, cap=None)
    c12 = c12_except + shakai_capped

    if c12 < 74:
        suggest12 = _names(sets12_except_shakai + shakai_all)
        errors.append(CheckError(
            12, "展開（情報・数理・多言語・世界理解ほか）合計74単位以上",
            have=c12, need=74, lack=74 - c12, suggest=suggest12
        ))

    # 上限超過の注意喚起（任意だが便利）
    if shakai_raw > 10:
        errors.append(CheckError(
            98,
            "注意喚起です。：社会接続は卒業単位として最大10単位まで（超過分は計上されません）",
            have=shakai_raw, need=10, lack=0,
            detail=[f"超過：{shakai_raw - 10} 単位"]
        ))

    # ---------- チェック13：プロジェクト実践（必修と仮定） ----------
    proj = session.query(ClassT).filter(ClassT.kamokumei == "プロジェクト実践").all()
    if proj and all(not is_acq(r.kamokumei) for r in proj):
        errors.append(CheckError(13, "プロジェクト実践（必修）", have=0, need=1, lack=1, suggest=_names(proj)))

    # ---------- 総取得単位 124（社会接続の上限10を反映） ----------
    all_rows = session.query(ClassT).all()
    total_raw = sum(_to_credits(r.tani) for r in all_rows if is_acq(r.kamokumei))
    total_credits = total_raw - (shakai_raw - shakai_capped)  # 超過分を引く
    total_ok = total_credits >= TOTAL_NEED

    # dataclass -> dict（Jinjaで扱いやすく）
    def _asdict(e: CheckError):
        return {
            "code": e.code, "title": e.title,
            "have": e.have, "need": e.need, "lack": e.lack,
            "detail": e.detail or [], "suggest": e.suggest or []
        }

    req_errors = [_asdict(e) for e in errors]
    return {
        # テンプレで使う想定のキー
        "req_errors": req_errors,
        "total_credits": total_credits,
        "total_need": TOTAL_NEED,
        "total_ok": total_ok,

        # （任意）デバッグ用に残すと便利
        "social_credits_raw": shakai_raw,
        "social_credits_counted": shakai_capped,
        # 互換：もしコード側で errors を参照している箇所があれば
        "errors": req_errors,
    }
