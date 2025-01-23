import os
import re
import glob
from tqdm import tqdm
from typing import Any, Iterator
from langchain_core.documents import Document
from langchain.schema import Document
from langchain.document_loaders.base import BaseLoader
from pdf2image import convert_from_path


class PDFParser(BaseLoader):
    """
    PDF 파일을 파싱하고 이미지로 변환하는 클래스

    이 클래스는 PDF 파일을 이미지로 변환하고, 각 페이지를 파싱하여 Document 객체로 반환합니다.
    """

    def __init__(
        self,
        file_path: str,
        multimodal,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        PDFParser 클래스의 생성자

        :param file_path: PDF 파일 경로
        """
        super().__init__(*args, **kwargs)
        self.file_path = file_path
        self.parsing_llm = multimodal
        self.convert_pdf_to_images()

    def convert_pdf_to_images(self):
        """PDF 파일을 이미지로 변환하고 캐시 디렉토리에 저장합니다."""
        # .pdf_cache 폴더 생성
        cache_dir = ".pdf_cache"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        # PDF 파일 이름을 가져와 폴더 이름으로 사용
        pdf_name = os.path.splitext(os.path.basename(self.file_path))[0]
        self.metadata = {"source": pdf_name}
        # 이미지를 저장할 디렉토리 (.pdf_cache/pdf_name)
        self.output_dir = os.path.join(cache_dir, pdf_name)

        # 출력 디렉토리가 없으면 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # PDF를 이미지로 변환
        images = convert_from_path(self.file_path)

        # 변환된 이미지 수를 추적
        converted_count = 0

        # tqdm을 사용하여 진행 상황 표시
        for i, image in tqdm(
            enumerate(images), total=len(images), desc="페이지 변환 중"
        ):
            image_path = os.path.join(self.output_dir, f"page_{i}.png")

            # 이미지가 이미 존재하는지 확인
            if not os.path.exists(image_path):
                image.save(image_path, "PNG")
                converted_count += 1

        print(f"\n[변환완료] Total Count: {len(images)} Pages.")
        self.total_pages = len(images)

    def get_image_path(self, page_number: int) -> str:
        """
        주어진 페이지 번호에 해당하는 이미지 파일의 경로를 반환합니다.

        :param page_number: 페이지 번호
        :return: 이미지 파일 경로
        """
        return os.path.join(self.output_dir, f"page_{page_number}.png")

    def parse_pdf_by_page(self, page_number: int) -> Document:
        """
        주어진 페이지 번호의 PDF 페이지를 파싱하여 Document 객체로 반환합니다.

        :param page_number: 파싱할 페이지 번호
        :return: 파싱된 내용을 담은 Document 객체
        """
        metadata = self.metadata.copy()
        metadata["page_number"] = page_number
        return Document(
            page_content=self.parsing_llm.invoke(
                self.get_image_path(page_number), display_image=False
            ),
            metadata=metadata,
        )

    def parse_pdf(self, image_path: str) -> Document:
        return self.parsing_llm.invoke(image_path, display_image=False)

    def lazy_load(self) -> Iterator[Document]:
        """
        PDF의 각 페이지를 게으르게 로드하고 파싱하여 Document 객체를 생성합니다.
        이미 파싱된 .md 파일이 있으면 그 파일에서 내용을 불러옵니다.

        :return: Document 객체의 이터레이터
        """
        # .pdf_cache_output 폴더 생성
        output_dir = ".pdf_cache_output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # PDF 파일 이름을 가져와 폴더 이름으로 사용
        pdf_name = os.path.splitext(os.path.basename(self.file_path))[0]
        pdf_output_dir = os.path.join(output_dir, pdf_name)

        # PDF 출력 디렉토리가 없으면 생성
        if not os.path.exists(pdf_output_dir):
            os.makedirs(pdf_output_dir)

        files = sorted(glob.glob(self.output_dir + "/*.png"))

        for file in tqdm(files, total=len(files), desc="PDF 처리중"):
            # 파일 이름에서 페이지 번호 추출
            page_number = int(re.search(r"page_(\d+)", os.path.basename(file)).group(1))

            md_filename = os.path.splitext(os.path.basename(file))[0] + ".md"
            md_filepath = os.path.join(pdf_output_dir, md_filename)
            metadata = self.metadata.copy() if hasattr(self, "metadata") else {}
            metadata["page"] = page_number

            if os.path.exists(md_filepath):
                # 이미 .md 파일이 존재하면 그 내용을 읽어옴
                with open(md_filepath, "r", encoding="utf-8") as md_file:
                    content = md_file.read()
                yield Document(page_content=content, metadata=metadata)
            else:
                # .md 파일이 없으면 페이지를 파싱하고 결과를 저장
                parsed_document = self.parse_pdf(file)

                with open(md_filepath, "w", encoding="utf-8") as md_file:
                    md_file.write(parsed_document)

                yield Document(page_content=parsed_document, metadata=metadata)
