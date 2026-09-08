from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from pydantic import BaseModel, Field
from typing import Optional

# Define the strict structure for the marketplace catalog
class SupplierSKU(BaseModel):
    brand_name: str = Field(description="The brand or manufacturer name")
    product_title: str = Field(description="The full name of the product")
    category: str = Field(description="Must be 'Auto Care', 'Home Improvement', or 'Other'")
    pack_size: str = Field(description="Weight, volume, or unit count (e.g., '500ml', 'Pack of 4')")
    base_cost: float = Field(description="The wholesale price or cost per unit as a numeric float")
    country_of_origin: Optional[str] = Field(description="Where the product was manufactured, if stated")

import os
from langchain_community.document_loaders import PyPDFLoader, UnstructuredEmailLoader, UnstructuredExcelLoader

def load_supplier_document(file_path: str):
    # Extract the file extension to determine the document type
    _, file_extension = os.path.splitext(file_path)
    ext = file_extension.lower()

    # Route to the appropriate LangChain loader
    if ext == ".pdf":
        print(f"📄 Detected PDF. Extracting text layers from {file_path}...")
        loader = PyPDFLoader(file_path)
        
    elif ext in [".eml", ".msg"]:
        print(f"📧 Detected Email. Stripping headers and extracting body from {file_path}...")
        loader = UnstructuredEmailLoader(file_path)
        
    elif ext in [".xlsx", ".xls"]:
        print(f"📊 Detected Spreadsheet. Reading scattered matrix cells from {file_path}...")
        # 'elements' mode handles disorganized sheets better than strict table parsing
        loader = UnstructuredExcelLoader(file_path, mode="elements")
        
    else:
        raise ValueError(f"Unsupported supplier file format: {ext}")

    # Execute the extraction and return the raw text chunks
    return loader.load()

def extract_sku_data(raw_documents):
    print("🧠 Processing unstructured text through Gemini...")
    
    # Combine all extracted text chunks into a single string
    full_text = "\n".join([doc.page_content for doc in raw_documents])
    
    # Initialize the LLM with a temperature of 0 to eliminate hallucinations
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    # Bind the Pydantic schema to the model to enforce the exact output structure
    structured_llm = llm.with_structured_output(SupplierSKU)
    
    prompt = PromptTemplate.from_template(
        "You are a meticulous retail catalog data entry clerk. "
        "Extract the core product details from the following raw supplier text. "
        "If a specific data point is completely missing, leave it blank or default to 0.0 for numbers.\n\n"
        "Supplier Text:\n{text}"
    )
    
    # Wire the prompt directly to the structured LLM
    chain = prompt | structured_llm
    
    # Execute the chain and return the validated Pydantic object
    validated_data = chain.invoke({"text": full_text})
    return validated_data

def calculate_retail_economics(sku: SupplierSKU) -> dict:
    # Define target margins based on retail categories
    category_margins = {
        "Auto Care": 0.40,
        "Home Improvement": 0.50,
        "Other": 0.35
    }
    
    # Retrieve the target margin for the extracted category
    target_margin = category_margins.get(sku.category, 0.35)
    
    # Calculate Minimum Retail Price: Cost / (1 - Margin)
    try:
        min_retail_price = sku.base_cost / (1 - target_margin)
    except ZeroDivisionError:
        min_retail_price = 0.0
        
    return {
        "Target Margin": f"{int(target_margin * 100)}%",
        "Base Cost": f"${sku.base_cost:.2f}",
        "Minimum Retail Price": f"${min_retail_price:.2f}"
    }

import pandas as pd

if __name__ == "__main__":
    from langchain_core.documents import Document
    
    print("\n🚀 Starting Batch Marketplace Ingestion...")
    
    # Simulating a batch of unstructured pitches
    supplier_pitches = [
        "TurtleWax Pro Auto Polish (500ml). USA. Wholesale $4.50.",
        "Meguiar's Ceramic Spray Wax (32 oz). Cost is $8.20 per unit.",
        "Armor All Glass Cleaner 16oz pack. $2.15 cost. Origin: Mexico."
    ]
    
    catalog_database = []
    
    for pitch in supplier_pitches:
        print(f"\nProcessing pitch: {pitch[:30]}...")
        doc = [Document(page_content=pitch)]
        
        try:
            # Extract and validate
            sku_data = extract_sku_data(doc)
            economics = calculate_retail_economics(sku_data)
            
            # Combine Pydantic fields and economics into a single dictionary
            row = sku_data.model_dump()
            row.update(economics)
            
            catalog_database.append(row)
        except Exception as e:
            print(f"Failed to process item: {e}")
            
    # Export to CSV using Pandas
    print("\n💾 Exporting to Catalog CSV...")
    df = pd.DataFrame(catalog_database)
    df.to_csv("marketplace_new_skus.csv", index=False)
    print("✅ Export complete. Check marketplace_new_skus.csv in your folder.")