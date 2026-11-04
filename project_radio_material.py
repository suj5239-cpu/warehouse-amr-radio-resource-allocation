import drjit as dr
import mitsuba as mi

from sionna.rt import (
    InteractionType,
    RadioMaterialBase,
)
from sionna.rt.constants import NO_JONES_MATRIX
from sionna.rt.utils import (
    jones_matrix_to_world_implicit,
    isclose,
)


# XML에 기록할 고정된 재질 plugin 이름
PLUGIN_NAME = "project-radio-material-v1"

class ProjectRadioMaterial(RadioMaterialBase):
    '''Reflection-only or transmission-only project material.'''

    REFLECT = 1
    TRANSMIT = 0

    def __init__(self, name=None, mode=TRANSMIT, rho=0.0,
                 alpha_db_per_m=0.0, thickness=0.1,
                 color=None, props=None):
        if props is None:
            props = mi.Properties(PLUGIN_NAME)
            props.set_id(name)
            props["mode"] = int(mode)
            props["rho"] = float(rho)
            props["alpha_db_per_m"] = float(alpha_db_per_m)
            props["thickness"] = float(thickness)
            if color is not None:
                props["color"] = mi.ScalarColor3f(color)

        self._mode = int(props["mode"]) if "mode" in props else self.TRANSMIT
        if "mode" in props:
            del props["mode"]

        rho_value = props["rho"] if "rho" in props else 0.0
        if "rho" in props:
            del props["rho"]
        self._rho = mi.Float(rho_value)

        alpha_value = props["alpha_db_per_m"] if "alpha_db_per_m" in props else 0.0
        if "alpha_db_per_m" in props:
            del props["alpha_db_per_m"]
        self._alpha_db_per_m = mi.Float(alpha_value)

        thickness_value = props["thickness"] if "thickness" in props else 0.1
        if "thickness" in props:
            del props["thickness"]
        self._thickness = mi.Float(thickness_value)

        super().__init__(props)

    @property
    def event(self):
        return (InteractionType.SPECULAR
                if self._mode == self.REFLECT
                else InteractionType.REFRACTION)

    def frequency_update(self):
        # alpha and rho are intentionally frequency-independent in this project.
        pass

    def _direction_and_amplitude(self, ki_local):
        if self._mode == self.REFLECT:
            ko_local = mi.reflect(-ki_local)
            amp = self._rho
        else:
            ko_local = ki_local
            cos_theta = dr.maximum(dr.abs(ki_local.z), mi.Float(1e-3))
            length = self._thickness / cos_theta
            amp = dr.exp(-dr.log(mi.Float(10.0))
                         * self._alpha_db_per_m * length / 20.0)
        return ko_local, amp

    def _jones(self, si, ki_local, ko_local, amp):
        to_world = mi.Matrix3f(
            si.sh_frame.s, si.sh_frame.t, si.sh_frame.n
        ).T
        c = mi.Complex2f(amp, 0.0)
        jones = jones_matrix_to_world_implicit(
            c1=c,
            c2=c,
            to_world=to_world,
            k_in_local=ki_local,
            k_out_local=ko_local,
        )
        return to_world, jones

    def sample(self, ctx, si, sample1, sample2, active=True):
        ki_local = si.wi
        ko_local, amp = self._direction_and_amplitude(ki_local)

        to_world = mi.Matrix3f(
            si.sh_frame.s,
            si.sh_frame.t,
            si.sh_frame.n,
        ).T

        # 필요한 경우에만 Jones matrix 계산
        compute_jones = (
            ctx.component & NO_JONES_MATRIX
        ) == 0

        if compute_jones:
            _, jones = self._jones(
                si,
                ki_local,
                ko_local,
                amp,
            )
            jones = mi.Spectrum(jones)
        else:
            jones = mi.Spectrum(0.0)

        # Sionna가 si.dp_du.z에 저장한
        # 활성화된 interaction 정보를 읽음
        enabled_interactions = dr.reinterpret_array(
            mi.UInt,
            si.dp_du.z,
        )

        enabled = (
            active
            & (
                (
                    enabled_interactions
                    & mi.UInt(self.event)
                ) > 0
            )
        )

        jones = dr.select(
            enabled,
            jones,
            0.0,
        )

        bs = mi.BSDFSample3f()

        bs.sampled_component = dr.select(
            enabled,
            mi.UInt(self.event),
            mi.UInt(InteractionType.NONE),
        )

        bs.wo = to_world @ ko_local

        bs.pdf = dr.select(
            enabled,
            mi.Float(1.0),
            mi.Float(0.0),
        )

        bs.sampled_type = mi.UInt32(
            +mi.BSDFFlags.DeltaReflection
        )
        bs.eta = 1.0

        return bs, jones


    def eval(self, ctx, si, wo, active=True):
        ki_local = si.wi
        ko_local, amp = self._direction_and_amplitude(
            ki_local
        )

        _, jones = self._jones(
            si,
            ki_local,
            ko_local,
            amp,
        )

        # wo는 WORLD frame으로 전달되므로 local로 변환해야 함
        wo_local = si.to_local(wo)
        direction_ok = isclose(
            dr.dot(ko_local, wo_local),
            mi.Float(1.0),
        )

        # 선택된 interaction type은 si.dp_du.z에 저장됨 (si.prim_index 아님)
        sampled_event = dr.reinterpret_array(
            mi.UInt,
            si.dp_du.z,
        )
        event_ok = sampled_event == mi.UInt(self.event)

        enabled = (
            active
            & direction_ok
            & event_ok
        )

        return mi.Spectrum(
            dr.select(enabled, jones, 0.0)
        )


    def pdf(self, ctx, si, wo, active=True):
        ki_local = si.wi
        ko_local, _ = self._direction_and_amplitude(
            ki_local
        )

        # wo는 WORLD frame으로 전달되므로 local로 변환해야 함
        wo_local = si.to_local(wo)
        direction_ok = isclose(
            dr.dot(ko_local, wo_local),
            mi.Float(1.0),
        )

        sampled_event = dr.reinterpret_array(
            mi.UInt,
            si.dp_du.z,
        )
        event_ok = sampled_event == mi.UInt(self.event)

        valid = (
            active
            & direction_ok
            & event_ok
        )

        return dr.select(
            valid,
            mi.Float(1.0),
            mi.Float(0.0),
        )

    
    def traverse(self, callback):
        callback.put("rho", self._rho, mi.ParamFlags.Differentiable)
        callback.put("alpha_db_per_m", self._alpha_db_per_m,
                     mi.ParamFlags.Differentiable)
        callback.put("thickness", self._thickness,
                     mi.ParamFlags.Differentiable)

    def to_string(self):
        role = "reflect" if self._mode == self.REFLECT else "transmit"
        return ("ProjectRadioMaterial["
                f"mode={role}, rho={self._rho}, "
                f"alpha_db_per_m={self._alpha_db_per_m}, "
                f"thickness={self._thickness}]")


mi.register_bsdf(
    PLUGIN_NAME,
    lambda props: ProjectRadioMaterial(props=props),
)
print("Registered Mitsuba BSDF plugin:", PLUGIN_NAME)