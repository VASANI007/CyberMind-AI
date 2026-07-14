"""
===========================================================
CyberMind AI
Database Schema
===========================================================
"""

SCHEMA = [

    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS scan_history (
        scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_type TEXT NOT NULL,
        target TEXT NOT NULL,
        risk_level TEXT CHECK (
            risk_level IN (
                'Safe',
                'Low',
                'Medium',
                'High',
                'Critical'
            )
        ),
        risk_score REAL DEFAULT 0,
        status TEXT DEFAULT 'Completed',
        scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        country TEXT,
        country_code TEXT,
        latitude REAL,
        longitude REAL
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS url_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        url TEXT,
        domain TEXT,
        https BOOLEAN,
        status_code INTEGER,
        response_time REAL,
        redirect_count INTEGER,
        server TEXT,
        content_type TEXT,
        google_safe_browsing TEXT,
        virustotal TEXT,
        risk_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scan_id)
            REFERENCES scan_history(scan_id)
            ON DELETE CASCADE
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS website_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        url TEXT,
        title TEXT,
        server TEXT,
        ssl_version TEXT,
        tls_version TEXT,
        security_headers TEXT,
        technologies TEXT,
        dns_records TEXT,
        risk_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scan_id)
            REFERENCES scan_history(scan_id)
            ON DELETE CASCADE
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS domain_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        domain TEXT,
        registrar TEXT,
        creation_date TEXT,
        expiration_date TEXT,
        updated_date TEXT,
        dnssec TEXT,
        whois_status TEXT,
        risk_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scan_id)
            REFERENCES scan_history(scan_id)
            ON DELETE CASCADE
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS email_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        email TEXT,
        provider TEXT,
        valid BOOLEAN,
        mx_record BOOLEAN,
        disposable BOOLEAN,
        free_provider BOOLEAN,
        risk_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scan_id)
            REFERENCES scan_history(scan_id)
            ON DELETE CASCADE
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS ip_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        ip TEXT,
        country TEXT,
        city TEXT,
        region TEXT,
        asn TEXT,
        isp TEXT,
        abuse_score REAL,
        latitude REAL,
        longitude REAL,
        risk_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scan_id)
            REFERENCES scan_history(scan_id)
            ON DELETE CASCADE
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS file_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        filename TEXT,
        extension TEXT,
        mime_type TEXT,
        file_size INTEGER,
        md5 TEXT,
        sha1 TEXT,
        sha256 TEXT,
        signature TEXT,
        virustotal TEXT,
        risk_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scan_id)
            REFERENCES scan_history(scan_id)
            ON DELETE CASCADE
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS qr_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER NOT NULL,
        payload TEXT,
        qr_type TEXT,
        decoded_text TEXT,
        is_short_url BOOLEAN,
        contains_url BOOLEAN,
        risk_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scan_id)
            REFERENCES scan_history(scan_id)
            ON DELETE CASCADE
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS api_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_name TEXT,
        request_url TEXT,
        status_code INTEGER,
        response_time REAL,
        success BOOLEAN,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_name TEXT,
        report_type TEXT,
        report_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS scan_statistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_date DATE,
        total_scans INTEGER DEFAULT 0,
        safe INTEGER DEFAULT 0,
        low INTEGER DEFAULT 0,
        medium INTEGER DEFAULT 0,
        high INTEGER DEFAULT 0,
        critical INTEGER DEFAULT 0
    );
    """
]