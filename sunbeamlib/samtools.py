""" Helper functions for working with samtools. """

import subprocess
import numpy
import csv

def get_coverage_stats(genome_name, bamfiles, sample_names, output_fp):
    """Produce a CSV table of alignment stats for a single genome.
    
    genome_name: identifier for genome
    bamfiles: list of file paths to BAM files
    sample_names: list of idenifiers for the sample for each BAM file
    output_fp: path to CSV output file

    There's lot of redundant information (genome name on every row, segment
    name and stats across all relevant rows) but it makes the results a bit
    easier to work with.
    """
    output_rows = []
    for bamfile, sample in sorted(zip(bamfiles, sample_names)):
        # Get coverage depth at each position, even if zero across whole segment
        p = subprocess.Popen(["samtools", "depth", "-aa", bamfile], stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        # Organize into a list of depths for each segment
        lines = str(stdout, 'ascii').splitlines()
        reader = csv.reader(lines, delimiter='\t')
        data = {}
        for row in reader:
            if not data.get(row[0]):
                data[row[0]] = []
            data[row[0]].append(int(row[2]))
        # Summarize stats for all segments present and append to output
        for segment in data.keys():
            minval     = numpy.min(data[segment])
            maxval     = numpy.max(data[segment])
            mean       = numpy.mean(data[segment])
            median     = numpy.median(data[segment])
            stddev     = numpy.std(data[segment])
            gen_cov    = len(list(filter(lambda x: x!=0, data[segment])))
            gen_length = len(data[segment])
            row = [genome_name, segment, sample, minval, maxval, mean, median, stddev, gen_cov, gen_length]
            output_rows.append(row)
    # write out stats per segment per sample
    fields = ['Genome', 'Segment', 'Sample', 'Min', 'Max', 'Mean', 'Median', 'Std Dev', 'Segment Coverage', 'Segment Length']
    with open(output_fp, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        writer.writerows(output_rows)
