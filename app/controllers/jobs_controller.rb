require 'httparty'

class JobsController < ApplicationController
  def index
    # Render the form to collect user preferences
  end

  def recommend_jobs
    user_input = {
      personality: params[:personality],
      work_experience: params[:work_experience],
      work_hours: params[:work_hours],
      salary: params[:salary], 
      skills: params[:skills]   
    }

    
    api_url = 'http://localhost:5000/recommend_jobs'
    begin
      response = HTTParty.post(api_url, body: user_input.to_json, headers: { 'Content-Type' => 'application/json' })

      if response.success?
        
        begin
          @recommended_jobs = JSON.parse(response.body)
          @recommended_jobs = [] if @recommended_jobs.nil? || !@recommended_jobs.is_a?(Array)

         
          @recommended_jobs = @recommended_jobs.sort_by { |job| -job['accuracy_percentage'] }.first(3)
          
          
          redirect_to recommended_jobs_path(recommended_jobs: @recommended_jobs)
        rescue JSON::ParserError => e
          flash[:alert] = "Error parsing the response from the API: #{e.message}"
          redirect_to jobs_path
        end
      else
        flash[:alert] = "API request failed with status #{response.code}"
        redirect_to jobs_path
      end
    rescue StandardError => e
      flash[:alert] = "An error occurred while making the API request: #{e.message}"
      redirect_to jobs_path
    end
  end

  def recommended_jobs
    @recommended_jobs = params[:recommended_jobs]
  end
end
