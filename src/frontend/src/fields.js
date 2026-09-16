// Field metadata for the 41 NSL-KDD connection-record features, grouped the
// same way the NSL-KDD/KDD Cup literature groups them: basic connection
// features, content features (inside the payload), time-based traffic
// features, and host-based traffic features. This mirrors NetworkLogRecord
// in the backend's src/backend/schemas.py -- keep the two in sync if either
// changes.

export const PROTOCOL_TYPES = ["tcp", "udp", "icmp"];

// The full flag vocabulary the training data's OneHotEncoder was fit on.
export const FLAGS = ["SF", "S0", "S1", "S2", "S3", "REJ", "RSTO", "RSTR", "RSTOS0", "SH", "OTH"];

// Not exhaustive (NSL-KDD has ~70 service values) -- just common ones for
// the datalist. Anything else is still accepted: the backend's encoder was
// fit with handle_unknown="ignore", so an unseen service value is encoded
// as all-zeros instead of erroring.
export const COMMON_SERVICES = [
  "http", "ftp", "ftp_data", "smtp", "telnet", "ssh", "domain_u", "private",
  "eco_i", "ecr_i", "other", "pop_3", "finger", "http_443", "auth", "time",
];

const int = (name, label, opts = {}) => ({ name, label, type: "number-int", step: 1, min: 0, ...opts });
const rate = (name, label, opts = {}) => ({ name, label, type: "number-float", step: 0.01, min: 0, max: 1, ...opts });

export const FIELD_GROUPS = [
  {
    title: "Basic connection features",
    help: "Fundamental attributes of a single TCP/UDP/ICMP connection.",
    fields: [
      { name: "protocol_type", label: "Protocol type", type: "select", options: PROTOCOL_TYPES },
      { name: "service", label: "Service", type: "text-suggest", options: COMMON_SERVICES },
      { name: "flag", label: "Connection flag", type: "select", options: FLAGS },
      int("duration", "Duration (seconds)"),
      int("src_bytes", "Source bytes"),
      int("dst_bytes", "Destination bytes"),
      { name: "land", label: "Land attack (src == dst)", type: "select", options: ["0", "1"] },
      int("wrong_fragment", "Wrong fragments"),
      int("urgent", "Urgent packets"),
    ],
  },
  {
    title: "Content features",
    help: "Signals from inside the connection payload, mostly relevant to R2L/U2R-style attacks.",
    fields: [
      int("hot", "Hot indicators"),
      int("num_failed_logins", "Failed logins"),
      { name: "logged_in", label: "Logged in successfully", type: "select", options: ["0", "1"] },
      int("num_compromised", "Compromised conditions"),
      { name: "root_shell", label: "Root shell obtained", type: "select", options: ["0", "1"] },
      { name: "su_attempted", label: "'su root' attempted", type: "select", options: ["0", "1"] },
      int("num_root", "Root accesses"),
      int("num_file_creations", "File creation operations"),
      int("num_shells", "Shell prompts"),
      int("num_access_files", "Operations on access control files"),
      int("num_outbound_cmds", "Outbound commands (FTP sessions)"),
      { name: "is_host_login", label: "Login belongs to 'hot' list", type: "select", options: ["0", "1"] },
      { name: "is_guest_login", label: "Guest login", type: "select", options: ["0", "1"] },
    ],
  },
  {
    title: "Time-based traffic features",
    help: "Computed over connections to the same host in the past 2 seconds.",
    fields: [
      int("count", "Connections to same host"),
      int("srv_count", "Connections to same service"),
      rate("serror_rate", "SYN error rate"),
      rate("srv_serror_rate", "Service SYN error rate"),
      rate("rerror_rate", "REJ error rate"),
      rate("srv_rerror_rate", "Service REJ error rate"),
      rate("same_srv_rate", "Same-service rate"),
      rate("diff_srv_rate", "Different-service rate"),
      rate("srv_diff_host_rate", "Different-host rate (same service)"),
    ],
  },
  {
    title: "Host-based traffic features",
    help: "Same idea as above, but computed over a window of the last 100 connections to the same destination host.",
    fields: [
      int("dst_host_count", "Dest. host connections"),
      int("dst_host_srv_count", "Dest. host service connections"),
      rate("dst_host_same_srv_rate", "Dest. host same-service rate"),
      rate("dst_host_diff_srv_rate", "Dest. host different-service rate"),
      rate("dst_host_same_src_port_rate", "Dest. host same-src-port rate"),
      rate("dst_host_srv_diff_host_rate", "Dest. host srv different-host rate"),
      rate("dst_host_serror_rate", "Dest. host SYN error rate"),
      rate("dst_host_srv_serror_rate", "Dest. host service SYN error rate"),
      rate("dst_host_rerror_rate", "Dest. host REJ error rate"),
      rate("dst_host_srv_rerror_rate", "Dest. host service REJ error rate"),
    ],
  },
];

// Two illustrative starting points -- NOT records pulled from the dataset,
// just plausible values so the form isn't empty and the demo has a
// one-click "obviously normal" / "obviously suspicious" contrast. Every
// field is still editable before submitting.
export const EXAMPLE_NORMAL = {
  duration: 0, protocol_type: "tcp", service: "http", flag: "SF",
  src_bytes: 215, dst_bytes: 45076, land: 0, wrong_fragment: 0,
  urgent: 0, hot: 0, num_failed_logins: 0, logged_in: 1,
  num_compromised: 0, root_shell: 0, su_attempted: 0, num_root: 0,
  num_file_creations: 0, num_shells: 0, num_access_files: 0,
  num_outbound_cmds: 0, is_host_login: 0, is_guest_login: 0,
  count: 1, srv_count: 1, serror_rate: 0.0, srv_serror_rate: 0.0,
  rerror_rate: 0.0, srv_rerror_rate: 0.0, same_srv_rate: 1.0,
  diff_srv_rate: 0.0, srv_diff_host_rate: 0.0, dst_host_count: 1,
  dst_host_srv_count: 1, dst_host_same_srv_rate: 1.0,
  dst_host_diff_srv_rate: 0.0, dst_host_same_src_port_rate: 0.0,
  dst_host_srv_diff_host_rate: 0.0, dst_host_serror_rate: 0.0,
  dst_host_srv_serror_rate: 0.0, dst_host_rerror_rate: 0.0,
  dst_host_srv_rerror_rate: 0.0,
};

// Loosely modeled on a "neptune" (SYN-flood) style record: many
// near-simultaneous connection attempts to one service, almost all of them
// erroring out (high serror_rate), low same_srv_rate.
export const EXAMPLE_ATTACK = {
  duration: 0, protocol_type: "tcp", service: "private", flag: "S0",
  src_bytes: 0, dst_bytes: 0, land: 0, wrong_fragment: 0,
  urgent: 0, hot: 0, num_failed_logins: 0, logged_in: 0,
  num_compromised: 0, root_shell: 0, su_attempted: 0, num_root: 0,
  num_file_creations: 0, num_shells: 0, num_access_files: 0,
  num_outbound_cmds: 0, is_host_login: 0, is_guest_login: 0,
  count: 123, srv_count: 6, serror_rate: 1.0, srv_serror_rate: 1.0,
  rerror_rate: 0.0, srv_rerror_rate: 0.0, same_srv_rate: 0.05,
  diff_srv_rate: 0.07, srv_diff_host_rate: 0.0, dst_host_count: 255,
  dst_host_srv_count: 26, dst_host_same_srv_rate: 0.1,
  dst_host_diff_srv_rate: 0.05, dst_host_same_src_port_rate: 0.0,
  dst_host_srv_diff_host_rate: 0.0, dst_host_serror_rate: 1.0,
  dst_host_srv_serror_rate: 1.0, dst_host_rerror_rate: 0.0,
  dst_host_srv_rerror_rate: 0.0,
};

export const ALL_FIELDS = FIELD_GROUPS.flatMap((group) => group.fields);
