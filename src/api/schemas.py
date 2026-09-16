from pydantic import BaseModel, ConfigDict


class NetworkLogRecord(BaseModel):
    """One network connection record, matching the 41 official NSL-KDD
    features (everything data_loader.COLUMNS has except 'target' and
    'difficulty_level', which are ground-truth/metadata, not model inputs).

    protocol_type, service, and flag are sent as raw strings -- the API
    applies the same fitted OneHotEncoder used at training time before
    scoring, so callers never need to encode anything themselves.
    """

    duration: int
    protocol_type: str
    service: str
    flag: str
    src_bytes: int
    dst_bytes: int
    land: int
    wrong_fragment: int
    urgent: int
    hot: int
    num_failed_logins: int
    logged_in: int
    num_compromised: int
    root_shell: int
    su_attempted: int
    num_root: int
    num_file_creations: int
    num_shells: int
    num_access_files: int
    num_outbound_cmds: int
    is_host_login: int
    is_guest_login: int
    count: int
    srv_count: int
    serror_rate: float
    srv_serror_rate: float
    rerror_rate: float
    srv_rerror_rate: float
    same_srv_rate: float
    diff_srv_rate: float
    srv_diff_host_rate: float
    dst_host_count: int
    dst_host_srv_count: int
    dst_host_same_srv_rate: float
    dst_host_diff_srv_rate: float
    dst_host_same_src_port_rate: float
    dst_host_srv_diff_host_rate: float
    dst_host_serror_rate: float
    dst_host_srv_serror_rate: float
    dst_host_rerror_rate: float
    dst_host_srv_rerror_rate: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "duration": 0, "protocol_type": "tcp", "service": "http", "flag": "SF",
                "src_bytes": 215, "dst_bytes": 45076, "land": 0, "wrong_fragment": 0,
                "urgent": 0, "hot": 0, "num_failed_logins": 0, "logged_in": 1,
                "num_compromised": 0, "root_shell": 0, "su_attempted": 0, "num_root": 0,
                "num_file_creations": 0, "num_shells": 0, "num_access_files": 0,
                "num_outbound_cmds": 0, "is_host_login": 0, "is_guest_login": 0,
                "count": 1, "srv_count": 1, "serror_rate": 0.0, "srv_serror_rate": 0.0,
                "rerror_rate": 0.0, "srv_rerror_rate": 0.0, "same_srv_rate": 1.0,
                "diff_srv_rate": 0.0, "srv_diff_host_rate": 0.0, "dst_host_count": 1,
                "dst_host_srv_count": 1, "dst_host_same_srv_rate": 1.0,
                "dst_host_diff_srv_rate": 0.0, "dst_host_same_src_port_rate": 0.0,
                "dst_host_srv_diff_host_rate": 0.0, "dst_host_serror_rate": 0.0,
                "dst_host_srv_serror_rate": 0.0, "dst_host_rerror_rate": 0.0,
                "dst_host_srv_rerror_rate": 0.0,
            }
        }
    )


class PredictionResponse(BaseModel):
    """Response returned by POST /predict."""

    classification: str  # "normal" or "attack"
    label: int            # 0 = normal, 1 = attack -- same encoding train.py used
    risk_score: float     # model's predicted probability of the "attack" class
