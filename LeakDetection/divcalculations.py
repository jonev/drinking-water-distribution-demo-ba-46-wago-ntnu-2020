class DivCalculations:
    def __init__(self):
        pass

    @staticmethod
    def avgValue(samples, value_column_nr):
        if len(samples) < 1:
            return 0
        sample_sum = 0
        for sample in samples:
            sample_sum = sample_sum + sample[value_column_nr]
        avg_value = sample_sum / len(samples)
        return avg_value
