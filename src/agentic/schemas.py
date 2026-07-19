from pydantic import BaseModel, Field

class SaveNoteSchema(BaseModel):
    title: str = Field(description="The unique title of the note. Must be concise.")
    content: str = Field(description="The actual text content to save.")

class DeleteNoteSchema(BaseModel):
    title: str = Field(description="The exact title of the note to delete.")

class SearchNotesSchema(BaseModel):
    query: str = Field(description="A keyword or phrase to search for across all saved notes.")

class SummarizeNotesSchema(BaseModel):
    topic: str = Field(description="The overarching topic to summarize based on saved notes.")