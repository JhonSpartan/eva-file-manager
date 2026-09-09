class CloudDatabaseMigrator:

    CURRENT_VERSION = 1

    def migrate(self, connection) -> None:
        self.ensure_schema_version_table(connection)

        current_version = self.get_current_version(
            connection
        )

        if current_version < 1:
            self.migrate_to_v1(
                connection
            )

            self.set_version(
                connection,
                1,
            )

    def ensure_schema_version_table(
            self,
            connection,
    ) -> None:

        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER NOT NULL
                )
            """)

            cursor.execute("""
                SELECT version
                FROM schema_version
                LIMIT 1
            """)

            row = cursor.fetchone()

            if row is None:
                cursor.execute("""
                    INSERT INTO schema_version (
                        version
                    )
                    VALUES (0)
                """)

    def get_current_version(
            self,
            connection,
    ) -> int:

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT version
                FROM schema_version
                LIMIT 1
            """)

            row = cursor.fetchone()

            return int(row[0])

    def set_version(
            self,
            connection,
            version: int,
    ) -> None:

        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE schema_version
                SET version = %s
                """,
                (version,),
            )

    def migrate_to_v1(
            self,
            connection,
    ) -> None:

        with connection.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS copy_rules (
                    id BIGSERIAL PRIMARY KEY,
                    mode TEXT NOT NULL,
                    from_id TEXT NOT NULL,
                    to_id TEXT NOT NULL,
                    uuid UUID NOT NULL UNIQUE,
                    updated_at TIMESTAMPTZ NOT NULL,
                    deleted_at TIMESTAMPTZ,
                    UNIQUE(mode, from_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS template_catalog (
                    id BIGSERIAL PRIMARY KEY,
                    folder_id INTEGER NOT NULL,
                    template_name TEXT NOT NULL,
                    has_stoppers INTEGER NOT NULL DEFAULT 0,
                    uuid UUID NOT NULL UNIQUE,
                    updated_at TIMESTAMPTZ NOT NULL,
                    deleted_at TIMESTAMPTZ,
                    UNIQUE(folder_id, template_name)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stopper_catalog (
                    id BIGSERIAL PRIMARY KEY,
                    stopper_name TEXT NOT NULL UNIQUE,
                    diameter DOUBLE PRECISION NOT NULL,
                    uuid UUID NOT NULL UNIQUE,
                    updated_at TIMESTAMPTZ NOT NULL,
                    deleted_at TIMESTAMPTZ
                )
            """)