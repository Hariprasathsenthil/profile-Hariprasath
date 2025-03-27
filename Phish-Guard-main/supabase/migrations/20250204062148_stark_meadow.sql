/*
  # Create scans table for phishing detection results

  1. New Tables
    - `scans`
      - `id` (uuid, primary key)
      - `user_id` (uuid, references auth.users)
      - `url` (text)
      - `severity` (enum: low, medium, high)
      - `created_at` (timestamp)

  2. Security
    - Enable RLS on `scans` table
    - Add policies for authenticated users to:
      - Read their own scans
      - Create new scans
*/

-- Create enum type for severity levels
CREATE TYPE severity_level AS ENUM ('low', 'medium', 'high');

-- Create scans table
CREATE TABLE IF NOT EXISTS scans (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users NOT NULL,
  url text NOT NULL,
  severity severity_level NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can read own scans"
  ON scans
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create scans"
  ON scans
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- Create index for faster queries
CREATE INDEX scans_user_id_idx ON scans(user_id);
CREATE INDEX scans_created_at_idx ON scans(created_at DESC);