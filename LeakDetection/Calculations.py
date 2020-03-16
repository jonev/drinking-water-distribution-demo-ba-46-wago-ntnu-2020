class Calculations:
    def __init__(self):
        pass

    def avgValue(self, samples, value_column_nr):
        sample_sum = 0
        for sample in samples:
            sample_sum = sample_sum + sample[value_column_nr]
            avg_value = sample_sum / len(samples)
        print(avg_value)
        return avg_value
