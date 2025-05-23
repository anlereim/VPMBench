import csv
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Union

from vcf import Reader

from vpmbench import log
from vpmbench.data import EvaluationDataEntry, EvaluationData
from vpmbench.enums import PathogencityClass, VariationType, ReferenceGenome


class Extractor(ABC):
    """ Extractors are used to extract the :class:`~vpmbench.data.EvaluationData` from evaluation input files.

    """

    @abstractmethod
    def _extract(self, file_path: str) -> EvaluationData:
        """ Internal function to extract the evaluation data from the evaluation input file at `file-path`.

        This function has to be implemented for every extractor.

        Parameters
        ----------
        file_path
            The file path to evaluation input data

        Returns
        -------
        EvaluationData
            The evaluation data
        """
        raise NotImplementedError

    def extract(self, file_path: Union[str, Path]) -> EvaluationData:
        """ Extract the :class:`~vpmbench.data.EvaluationData` from the file at `file_path`.

        This function calls :meth:`~vpmbench.extractor.Extractor._extract` and uses
        :meth:`vpmbench.data.EvaluationData.validate` to check if the evaluation data is valid.

        Parameters
        ----------
        file_path
            The file path to evaluation input data


        Returns
        -------
        EvaluationData
            The validated evaluation data

        Raises
        ------
        RuntimeError
            If the file can not be parsed

        SchemaErrors
            If the validation of the extracted data fails

        """
        extraction_path = file_path
        try:
            extraction_path = str(extraction_path.resolve())
        except Exception:
            pass
        try:
            table = self._extract(extraction_path)
        except Exception as ex:
            raise RuntimeError(
                f"Can't parse data at '{file_path}' with '{self.__class__.__name__}'. \nMaybe the data does not exist, or is not "
                f"compatible with the Extractor.\n If the data exists use absolute path.") from ex
        log.debug("Extracted Data:")
        log.debug(table.variant_data.head(10))
        table.validate()
        return table


class CSVExtractor(Extractor):

    def __init__(self, row_to_entry_func=None, **kwargs) -> None:
        super().__init__()
        self.row_to_entry_func = self._row_to_evaluation_data_entry if row_to_entry_func is None else row_to_entry_func
        self.csv_reader_args = kwargs

    def _row_to_evaluation_data_entry(self, data_row) -> EvaluationDataEntry:
        raise NotImplementedError()

    def _extract(self, file_path: str) -> EvaluationData:
        records = []
        with open(file_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file, **self.csv_reader_args)
            for row in csv_reader:
                records.append(self.row_to_entry_func(row))
        return EvaluationData.from_records(records)


class VariSNPExtractor(CSVExtractor):
    """ An implementation of an :class:`~vpmbench.extractor.Extractor` for VariSNP files.
    """

    def __init__(self) -> None:
        super().__init__()
        self.csv_reader_args = {'delimiter': '\t'}

    def _row_to_evaluation_data_entry(self, data_row) -> EvaluationDataEntry:
        hgvs_name = data_row['hgvs_names'].split(";")[0]
        chrom_number = int(hgvs_name.split(":")[0][3:9])
        chrom = None
        if chrom_number <= 22:
            chrom = str(chrom_number)
        elif chrom_number == 23:
            chrom = "X"
        elif chrom_number == 24:
            chrom = "Y"
        pos = int(data_row['asn_to']) + 1
        alt = data_row['minor_allele']
        ref = data_row['reference_allele']
        return EvaluationDataEntry(chrom, pos, ref, alt, PathogencityClass.BENIGN, VariationType.SNP,
                                   ReferenceGenome.HG38)


class VCFExtractor(Extractor):

    def __init__(self, record_to_pathogencity_class_func=None) -> None:
        super().__init__()
        self.record_to_pathogencity_class_func = self._extract_pathogencity_class_from_record if record_to_pathogencity_class_func is None else record_to_pathogencity_class_func

    def _extract_pathogencity_class_from_record(self, vcf_record) -> PathogencityClass:
        raise NotImplementedError

    def _extract(self, file_path: str) -> EvaluationData:
        records = []
        vcf_reader = Reader(filename=file_path, encoding="latin-1", strict_whitespace=True)
        for vcf_record in vcf_reader:
            chrom = str(vcf_record.CHROM)
            pos = vcf_record.POS
            ref = vcf_record.REF
            alt = (vcf_record.ALT[0] if len(vcf_record.ALT) == 1 else vcf_record.ALT).sequence
            clnsig = self.record_to_pathogencity_class_func(vcf_record)
            variation_type = VariationType(vcf_record.var_type)
            rg = ReferenceGenome.resolve(vcf_reader.metadata["reference"])
            records.append(EvaluationDataEntry(chrom, pos, ref, alt, clnsig, variation_type, rg))
        return EvaluationData.from_records(records)


class ClinVarVCFExtractor(VCFExtractor):
    """ An implementation of an :class:`~vpmbench.extractor.Extractor` for ClinVarVCF files.
    """

    def _extract_pathogencity_class_from_record(self, vcf_record) -> PathogencityClass:
        vcf_clnsig = vcf_record.INFO["CLNSIG"][0].lower()
        return PathogencityClass.resolve(vcf_clnsig)
