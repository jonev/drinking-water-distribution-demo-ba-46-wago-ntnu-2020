self.cursor = self.db.cursor()
        self.cursor.execute(
            "SELECT * FROM flowValueValues WHERE timestamp >= %s AND timestamp <=%s", (date1, date2)
        )

        self.day_ft_values = self.cursor.fetchall()
        for self.ft_value in self.day_ft_values: