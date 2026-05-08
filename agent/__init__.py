"""Agent package: I/O bridges between the substrate and the outside world."""
from agent.encoder_audio import freq_to_port_position, encode_block, decode_to_audio
from agent.audio_io import AudioIO
from agent.encoder_video import (
    downsample_frame,
    build_oriented_filter_bank,
    encode_frame,
    patch_to_port_position,
    feature_magnitude_to_frequency,
)
from agent.video_io import VideoIO
from agent.reward import RewardChannel
from agent.loop import AgentLoop

__all__ = [
    "AudioIO",
    "VideoIO",
    "RewardChannel",
    "AgentLoop",
    "freq_to_port_position",
    "encode_block",
    "decode_to_audio",
    "downsample_frame",
    "build_oriented_filter_bank",
    "encode_frame",
    "patch_to_port_position",
    "feature_magnitude_to_frequency",
]
